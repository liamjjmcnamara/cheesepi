#!/usr/bin/env python

import subprocess
import sys
import time
import re

import cheesepi

config = cheesepi.config.get_config()
interface= config['wlan']

def measure(dao):
	start_time = cheesepi.utils.now()
	op_output  = perform()
	end_time   = cheesepi.utils.now()
	#print op_output
	parsed_output = parse_output(op_output, start_time, end_time)
	#print parsed_output
	scan_digest = digest_scan(parsed_output, start_time, end_time)
	dao.write_op("wifi_scan", scan_digest)
	for ap in parsed_output:
		dao.write_op("wifi_ap", ap)

def perform():
	try:
		scan_output = subprocess.check_output(["iwlist", interface, "scanning"])
	except Exception as e:
		print "Error: iwlist does not seem to run: "+str(e)
		sys.exit(1)
	if "Interface doesn't support scanning" in scan_output:
		print "Error: Interface doesn't support scanning"
		sys.exit(1)
	#print scan_output
	return scan_output

def parse_output(text, start_time, end_time):
	rv=[]
	aps=text.split("Cell")
	aps.pop(0) # remove first
	for ap in aps: # over each AccessPoint
		#print ap
		ap=parse_ap(ap)
		ap["start_time"] = start_time
		rv.append(ap)
	return rv

def parse_ap(text):
	ap={}
	try:
		ap['ESSID']   = re.findall('ESSID:".*"', text)[0][7:-1]
	except:
		ap['ESSID']   = "" # No broadcast ESSID
	ap['channel'] = int(re.findall('Channel .*', text)[0][8:-1])
	ap['address'] = re.findall('Address: .*',text)[0][9:]
	try:
		ap['quality'] = int(re.findall('Quality=.*? ', text)[0][8:-5])
	except:
		ap['quality'] = -1
	ap['signal']  = int(re.findall('Signal level=.*',text)[0][13:-6])
	#print ap
	return ap


def digest_scan(aps, start_time, end_time):
	digest={}
	digest["start_time"] = start_time
	digest["end_time"]   = end_time

	channels = [0]*14 # number of WiFi channels
	# count channel presence
	for ap in aps:
		if ap['channel']<15: # only 2.4Ghz
			channels[ap['channel']] += 1
	for c in xrange(len(channels)):
		digest[str(c)] = channels[c]
	return digest


def aps_to_JSON(aps, start_time):
	values=[]
	for ap in aps:
		values.append([start_time, ap['ESSID'], ap['channel'], ap['address'], ap['quality'], ap['signal']])

	json = [{ "name" : "ap",
			"columns" : ["time","ESSID","channel","address","quality","signal"],
			"points" : values,
	}]
	return json



if __name__ == "__main__":
	# claim a database storage object
	dao = cheesepi.config.get_dao()

	scanForever=False
	if scanForever:
		while(True):
			measure(dao)
			time.sleep(300)
	else:
		measure(dao)

