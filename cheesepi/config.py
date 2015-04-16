#!/usr/bin/env python
""" Copyright (c) 2015, Swedish Institute of Computer Science
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
	  * Redistributions of source code must retain the above copyright
		notice, this list of conditions and the following disclaimer.
	  * Redistributions in binary form must reproduce the above copyright
		notice, this list of conditions and the following disclaimer in the
		documentation and/or other materials provided with the distribution.
	  * Neither the name of The Swedish Institute of Computer Science nor the
		names of its contributors may be used to endorse or promote products
		derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE SWEDISH INSTITUTE OF COMPUTER SCIENCE BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Authors: ljjm@sics.se
Testers:
Description: Handles all configuration file duties, including initialising
a local config file (if one does not exist, and initialising logging options
"""

import sys
import os
import re
import uuid
import logging

import cheesepi


# Globals
cheesepi_dir  = os.path.dirname(os.path.realpath(__file__))
config_file   = os.path.join(cheesepi_dir,"cheesepi.conf")
version_file  = os.path.join(cheesepi_dir,"version")
config        = None # instantiated later!


def main():
	print config


def get_config():
	config = {}
	lines  = read_config()
	for line in lines:
		# strip comment and badly formed lines
		if re.match('^\s*#', line) or not re.search('=',line):
			continue
		# print line
		(key, value) = line.split("=",2)
		config[clean(key)] = clean(value)
	config['cheesepi_dir']= cheesepi_dir
	config['config_file'] = config_file
	config['version']     = version()
	return config


def read_config():
	# ensure we have a config file to read
	create_default_config()

	try:
		fd = open(config_file)
		lines = fd.readlines()
		fd.close()
	except Exception as e:
		print "Error: can not read config file: "+str(e)
		# should copy from default location!
		sys.exit(1)
	return lines


def create_default_config():
	"""If config file does not exist, try to copy from default.
	   Also add a local secret to the file."""
	# is there already a local config file?
	if os.path.isfile(config_file):
		return
	default_config = os.path.join(cheesepi_dir,"cheesepi.default.conf")
	# Can we find the default config file?
	if os.path.isfile(default_config):
		secret = generate_secret()
		try:
			copyfile(default_config, config_file, "_SECRET_", secret)
		except:
			msg = "Problem copying files - check permissions of %" % cheesepi_dir
			logging.error(msg)
			print "Error: "+msg
			exit(1)
	else:
		print "Error: can not find default config file!"


def get_dao():
	if config_equal('database',"mongo"):
		return cheesepi.storage.dao_mongo.DAO_mongo()
	elif config_equal('database',"influx"):
		return cheesepi.storage.dao_influx.DAO_influx()
	elif config_equal('database',"mysql"):
		return cheesepi.storage.dao_mysql.DAO_mysql()
	elif config_equal('database',"null"):
		return cheesepi.storage.dao.DAO()
	# and so on for other database engines...

	print config['database']
	msg = "Fatal error: 'database' type not set to a valid value in config file, exiting."
	print msg
	logging.error(msg)
	exit(1)


def copyfile(from_file, to_file, occurance, replacement):
	"""Copy a file <from_file> to <to_file> replacing all occurrences"""
	print from_file, to_file, occurance, replacement
	with open(from_file, "rt") as fin:
		with open(to_file, "wt") as fout:
			for line in fin:
				fout.write(line.replace(occurance, replacement))


def generate_secret():
	"""Make a secret for this node, to use in signing data"""
	return str(uuid.uuid4())


def log(message):
	# should actually log message to a file
	print message


def version():
	version="repos"
	try:
		fd = open(version_file)
		lines = fd.readlines()
		fd.close()
		version = lines[0].strip()
	except:
		logging.warning("No version file!")
	return version


def config_defined(key):
	"""Is the specified key defined and true in the config object?"""
	key = clean(key)
	if key in config:
		return True
	return False


def config_equal(key, value):
	"""Is the specified key equal to the given value?"""
	key   = clean(key)
	value = clean(value)
	if key in config:
		if config[key]==value:
			return True
	return False


def config_true(config, key):
	"""Is the specified key defined and true in the config object?"""
	key = clean(key)
	if key in config:
		if config[key]=="true":
			return True
	return False


# clean the identifiers
def clean(id):
	return id.strip().lower()


# Some accounting to happen on every import (mostly for config file making)
config  = get_config()
if config_defined('logfile'):
	logfile = os.path.join(cheesepi_dir, config['logfile'])
	logging.basicConfig(filename=logfile, level=logging.INFO, format="%(asctime)s;%(levelname)s;%(message)s")


if __name__ == "__main__":
	main()
