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
import logging

import cheesepi as cp


# Globals
if 'HOME' in os.environ:
	home_dir = os.environ['HOME']
else:
	home_dir = "/root"
cheesepi_dir = os.path.dirname(os.path.realpath(__file__))
log_dir      = home_dir
config_file  = os.path.join(cheesepi_dir, "cheesepi.conf")

# Store log in user's home directory
log_file    = os.path.join(log_dir, ".cheesepi.log")
log_level  = logging.ERROR
log_stdout = False
log_formatter = logging.Formatter("%(asctime)s-%(name)s:%(levelname)s; %(message)s")
logging.basicConfig(filename=log_file, level=log_level, format=log_formatter)
logger = logging.getLogger(__file__)



def get_logger(source=""):
	"""Return logger for the specific file"""
	return logging.getLogger(source)

def update_logging():
	global log_file
	global log_level
	global log_stdout
	global log_formatter

	if config_defined('log_file'):
		# TODO should allow for log files in different directories, like /var/log
		filename = get('log_file')
		log_file = os.path.join(log_dir, filename)
	if config_defined('log_level'):
		log_level = int(get('log_level'))
	if config_defined('log_stdout'):
		log_stdout = config_true('log_stdout')
	if config_defined('log_format'):
		log_formatter = logging.Formatter(get('log_format'))

	# Get root logger
	root_logger = logging.getLogger()
	root_logger.setLevel(log_level)

	# Remove old handlers
	for handler in root_logger.handlers:
		root_logger.removeHandler(handler)

	if log_file is not None:
		# Add log_file handler
		file_handler = logging.FileHandler(log_file, 'a')
		file_handler.setFormatter(log_formatter)
		root_logger.addHandler(file_handler)

	if log_stdout:
		# Add stdout handler
		out_handler = logging.StreamHandler(sys.stdout)
		out_handler.setFormatter(log_formatter)
		root_logger.addHandler(out_handler)

def get_dao():
	if config_equal('database',"mongo"):
		return cp.storage.dao_mongo.DAO_mongo()
	elif config_equal('database',"influx08"):
		return cp.storage.dao_influx08.DAO_influx()
	elif config_equal('database',"influx09"):
		return cp.storage.dao_influx09.DAO_influx()
	elif config_equal('database',"mysql"):
		return cp.storage.dao_mysql.DAO_mysql()
	elif config_equal('database',"null"):
		return cp.storage.dao.DAO()
	# and so on for other database engines...

	msg = "Fatal error: 'database' type not set to a valid value in config file, exiting."
	logger.error("Database type: "+config['database']+"\n"+msg)
	exit(1)

def generate_uuid():
	"""Generate a uuid, to use for identification and data signing"""
	import uuid
	return str(uuid.uuid4())


def ensure_default_config(clobber=False):
	"""If config file does not exist, try to copy from default.
	   Also add a local secret to the file."""
	# is there already a local config file?
	if os.path.isfile(config_file) and not clobber:
		return

	print "Warning: Copying cheesepi.default.conf file to a local version: %s" % config_file
	default_config = os.path.join(cheesepi_dir,"cheesepi.default.conf")
	# Can we find the default config file?
	if os.path.isfile(default_config):
		uuid = generate_uuid()
		secret = generate_uuid()
		replace = {
			"_UUID_": uuid,
			"_SECRET_": secret,
		}
		try:
			copyfile(default_config, config_file, replace=replace)
		except Exception as e:
			print "Error: Problem copying config file - check permissions of %s\n%s" % (cheesepi_dir,e)
			exit(1)
	else:
		logger.error("Can not find default config file!")

def read_config():
	# ensure we have a config file to read
	ensure_default_config()
	try:
		fd = open(config_file)
		lines = fd.readlines()
		fd.close()
	except Exception as e:
		logger.error("Error: can not read config file: "+str(e))
		# should copy from default location!
		sys.exit(1)
	return lines

def get_config():
	import re
	config = {}
	lines  = read_config()
	for line in lines:
		# strip comment and badly formed lines
		if re.match('^\s*#', line) or not re.search('=',line):
			continue
		# logger.debug(line)
		(key, value_string) = line.split("=",1)
		value = value_string.strip()
		if value=="true":  value=True
		if value=="false": value=False
		config[clean(key)] = value
	config['cheesepi_dir'] = cheesepi_dir
	config['config_file']  = config_file
	config['version']      = version()
	return config


def create_default_schedule(schedule_filename):
	"""If schedule file does not exist, try to copy from default."""
	# is there already a local schedule file?
	print "Warning: Copying default schedule file to a local version"
	default_schedule = os.path.join(cheesepi_dir,"schedule.default.dat")
	# Can we find the default schedule file?
	if os.path.isfile(default_schedule):
		#try:
		copyfile(default_schedule, schedule_filename)
		#except Exception as e:
		#	msg = "Problem copying schedule file - check permissions of %s: %s" % (cheesepi_dir, str(e))
		#	logger.error(msg)
		#	exit(1)
	else:
		logger.error("Can not find default schedule file schedule.default.conf!")
		sys.exit(1)

def load_local_schedule():
	import json
	schedule_filename = os.path.join(cheesepi_dir, config['schedule'])
	if not os.path.isfile(schedule_filename):
		create_default_schedule(schedule_filename)

	lines = []
	with open(schedule_filename) as f:
		lines = f.readlines()

	schedule = []
	for l in lines:
		if l.strip()=="" or l.strip().startswith("#"):
			continue # skip this comment line
		try:
			spec = json.loads(l)
			schedule.append(spec)
		except:
			logger.error("JSON task spec not parsed: "+l)
			pass
	return schedule

def load_remote_schedule():
	"""See if we can grab a schedule from the central server
	this should (in future) include authentication"""
	import urllib2
	try:
		url = 'http://cheesepi.sics.se/schedule.dat'
		response = urllib2.urlopen(url)
		schedule = response.read()
		return schedule
	except urllib2.HTTPError as e:
		logger.error("The CheesePi controller server '%s' couldn\'t fulfill the request. Code: %s" % (url, str(e.code)))
	except urllib2.URLError as e:
		logger.error('We failed to reach the central server: '+e.reason)
	except:
		logger.error("Unrecognised problem when downloading remote schedule...")
	return None



def set_last_updated(dao=None):
	if dao==None:
		dao = get_dao()
	dao.write_user_attribute("last_updated",cp.utils.now())

def get_last_updated(dao=None):
	"""When did we last update our code from the central server?"""
	if dao==None:
		dao = get_dao()
	last_updated = dao.read_user_attribute("last_updated")
	# convert to seconds
	return last_updated

def get_update_period():
	"""How frequently should we update?"""
	return 259200

def should_update(dao=None):
	"""Should we update our code?"""
	if not config_true('auto_update'):
		return False
	last_updated = get_last_updated(dao)
	update_period = get_update_period()
	if (last_updated < (cp.utils.now()-update_period)):
		return True
	return False


def set_last_dumped(dao=None):
	if dao==None:
		dao = get_dao()
	dao.write_user_attribute("last_dumped", cp.utils.now())

def get_last_dumped(dao=None):
	"""When did we last dump our data to the central server?"""
	if dao==None:
		dao = get_dao()
	last_dumped = dao.read_user_attribute("last_dumped")
	# convert to seconds
	return last_dumped

def get_dump_period():
	"""How frequently should we dump?"""
	return 86400

def should_dump(dao=None):
	"""Should we update our code?"""
	last_dumped = get_last_dumped(dao)
	dump_period = get_dump_period()
	if (last_dumped < (cp.utils.now()-dump_period)):
		return True
	return False


def copyfile(from_file, to_file, replace={}):
	"""Copy a file <from_file> to <to_file> replacing all occurrences"""
	logger.info(from_file+" "+to_file+" "+ str(replace))
	with open(from_file, "rt") as fin, open(to_file, "wt") as fout:
		for line in fin:
			for occurence, replacement in replace.iteritems():
				line = line.replace(occurence, replacement)
			fout.write(line)


def get_controller():
	if "controller" in config:
		return config['controller']
	else:
		return "http://cheesepi.sics.se"

def get_cheesepi_dir():
	return config['cheesepi_dir']

def make_databases():
	cmd = get_cheesepi_dir()+"/install/make_influx_DBs.sh"
	logger.warn("Making databases: "+cmd)
	os.system(cmd)

def version():
	"""Which version of CheesePi are we running?"""
	with open(os.path.join(cheesepi_dir,'VERSION')) as f:
		return f.read().strip()

def get(key):
	key = clean(key)
	if key in config:
		return config[key]
	return None

def get_landmarks():
	"""Who shall we ping/httping?"""
	if not config_defined('landmarks'):
		return []
	landmark_string = config['landmarks']
	landmarks = landmark_string.split()
	return landmarks

def get_dashboard_port():
	# TODO: should read from config file
	return "8080"

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

def config_true(key):
	"""Is the specified key defined and true in the config object?"""
	key = clean(key)
	if key in config:
		if config[key]=="true":
			return True
	return False


# clean the identifiers
def clean(id):
	return id.strip().lower()

def main():
	from pprint import PrettyPrinter
	printer = PrettyPrinter(indent=4)
	printer.pprint(config)



# Some accounting to happen on every import (mostly for config file making)
config = get_config()
update_logging()

if __name__ == "__main__":
	main()
