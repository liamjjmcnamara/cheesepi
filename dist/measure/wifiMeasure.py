#!/usr/bin/env python

import subprocess
import sys
import os
import time
import re

from influxdb import InfluxDBClient

interface="wlan0"
client = InfluxDBClient('localhost', 8086, 'root', 'root', 'measurements')

def main():
    if scanForever=False
    if scanForever:
        while(True):
            doScan()
            time.sleep(300)
    else:
        doScan()

def doScan():
	start_time = time.time()
	scan_output = subprocess.check_output(["iwlist", interface, "scanning"])
	end_time = time.time()
	#print scan_output
	aps = parseScan(scan_output)
	saveScan(aps, start_time, end_time)

def parseScan(text):
	rv=[]
	aps=text.split("Cell")
	aps.pop(0) # remove first
	for ap in aps:
		#print ap
		ap=parseAp(ap)
		rv.append(ap)
	return rv

def parseAp(text):
	ap={}
	ap['ESSID']   = re.findall('ESSID:".*"', text)[0][7:-1]
	ap['channel'] = int(re.findall('Channel .*', text)[0][8:-1])
	ap['address'] = re.findall('Address: .*',text)[0][9:]
	ap['quality'] = int(re.findall('Quality=.*? ', text)[0][8:-5])
	ap['signal']  = int(re.findall('Signal level=.*',text)[0][13:-6])
	print ap
	return ap


def saveScan(aps, start_time, end_time):
	global client
	print "Saving...",aps

	scanJSON = scanToJSON(aps,start_time)
	print scanJSON
	client.write_points(scanJSON)
	apJSON = apsToJSON(aps, start_time)
	print apJSON
	client.write_points(apJSON)


def scanToJSON(aps, start_time):
	values = [0]*14
	# count channel presence
	for ap in aps:
		values[ap['channel']] += 1
	values.insert(0,start_time)
	columns = ["time"]
	columns.extend([str(x) for x in xrange(1,14+1)])
	json = [{ "name" : "scan",
    		"columns" : columns,
    		"points" : [ values ],
  	}]
	return json



def apsToJSON(aps, start_time):
	values=[]
	for ap in aps:
		values.append([start_time, ap['ESSID'], ap['channel'], ap['address'], ap['quality'], ap['signal']])

	json = [{ "name" : "ap",
    		"columns" : ["time","ESSID","channel","address","quality","signal"],
    		"points" : values,
  	}]
	return json



if __name__ == "__main__":
	main()
