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
"""

import sys
import json
import urllib2
import uuid
import time
import md5
import argparse

import cheesepi as cp
from cheesepi.tasks import *

logger = cp.config.get_logger(__name__)


# Command line tool, installed through set.py
def console_script():
	commands = ['start','stop','status']

	parser = argparse.ArgumentParser(prog='cheesepi')
	parser.add_argument('command', metavar='COMMAND', choices=commands, nargs='?', help="'start' or 'stop' one of the CheesePi components")
	parser.add_argument('option', metavar='OPTION', nargs='?', help='Options to the command')
	args = parser.parse_args()

	if args.command=="status":
		show_status()
		return

	if   args.option=='dispatcher': control_dispatcher(args.command)
	elif args.option=='influxdb':   control_influxdb(args.command)
	elif args.option=='dashboard':  control_dashboard(args.command)
	else:
		print "Error: unknown OPTION: %s" % args.option
		sys.exit(1)

def show_status():
	print "Current status..."
	print

def control_dispatcher(action):
	print "%s the dispatcher" % action
	if action=='start':
		cp.dispatcher.start()
	else:
		print "Error: action not yet implemented!"

def control_influxdb(action):
	print "%s influxdb" % action
	if action=='start':
		pass
	else:
		print "Error: action not yet implemented!"

def control_dashboard(action):
	print "%s the dashboard" % action
	if action=='start':
		pass
	else:
		print "Error: action not yet implemented!"



def build_json(dao, json_str):
	"""Build a Task object out of a JSON string spec"""
	spec = json.loads(json_str)
	return build_task(dao, spec)

def build_task(dao, spec):
	if not 'taskname' in spec:
		logger.error("No 'taskname' specified!")
		return None

	spec['taskname'] = spec['taskname'].lower()

	if spec['taskname']=='ping':
		return Ping(dao, spec)
	elif spec['taskname']=='httping':
		return Httping(dao, spec)
	elif spec['taskname']=='traceroute':
		return Traceroute(dao, spec)
	elif spec['taskname']=='dash':
		return Dash(dao, spec)
	elif spec['taskname']=='dns':
		return DNS(dao, spec)
	elif spec['taskname']=='throughput':
		return Throughput(dao, spec)
	elif spec['taskname']=='iperf':
		return iPerf(dao, spec)
	elif spec['taskname']=='beacon':
		return Beacon(dao, spec)
	elif spec['taskname']=='upload':
		return Upload(dao, spec)
	elif spec['taskname']=='status':
		return Status(dao, spec)
	elif spec['taskname']=='wifi':
		return Wifi(dao, spec)
	elif spec['taskname']=='dummy':
		return Dummy(dao, spec)
	else:
		raise Exception('Task name not specified! '+str(spec))


# time functions
def now():
	return time.time()
	#return int(datetime.datetime.utcnow().strftime("%s"))

def isARM():
	if "arm" in platform.machine():
		return True
	return False

# logging facilities
def write_file(ret, start_time, ethmac):
	filename = "./"+ethmac+str(start_time)+".txt"
	fd = open(filename, 'w')
	fd.write(ret)
	fd.close()


def get_MAC():
	"""Return the MAC of this device's first NIC"""
	return str(hex(uuid.getnode()))[2:]

def get_host_id():
	"""Return this host's ID"""
	return str(md5.new(get_MAC()).hexdigest())


#get our currently used MAC address
def getCurrMAC():
	ret =':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
	return ret


#get our source address
def get_SA():
	try:
		ret = urllib2.urlopen('http://ip.42.pl/raw').read()
	except Exception as e: # We may be offline
		logger.error("Unable to request ip.42.pl server's view of our IP, we may be offline: %s" % e)
		return "0.0.0.0"
	return ret

def get_temperature():
	"""Return the current temperature sensor, if possible"""
	filename = "/sys/class/thermal/thermal_zone0/temp"
	try:
		f = open(filename, 'r')
		data = f.read()
		return float(data.strip())
	except:
		pass
	return None

#
# Simple statistics to avoid numpy
#
def mean(data):
	"""Return the sample arithmetic mean of data."""
	n = len(data)
	if n < 1:
		raise ValueError('mean requires at least one data point')
	return sum(data)/n # in Python 2 use sum(data)/float(n)


def sumsq(data):
	"""Return sum of square deviations of sequence data."""
	c = mean(data)
	ss = sum((x-c)**2 for x in data)
	return ss


def stdev(data):
	"""Calculates the population standard deviation."""
	n = len(data)
	if n < 2:
		raise ValueError('variance requires at least two data points')
	ss = sumsq(data)
	pvar = ss/n # the population variance
	return pvar**0.5
