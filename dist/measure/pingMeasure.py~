#!/usr/bin/python 
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

Original authors: guulay@kth.se
Re-written by: urbanpe@kth.se
Testers:



Example usage:
python pingMeasure.py -save=False -size=30 -number=100 www.bbc.com www.sics.se www.svt.se
This is equal to:
ping -c 100 -s 30 www.bbc.com
ping -c 100 -s 30 www.sics.se
ping -c 100 -s 30 www.svt.se

If -save=True the program will attempt to write to a file named after the device's ethernet mac address + the current date. For example 00:aa:bb:cc:dd:ee 01:23:45.678901.txt if the mac address
for the ethernet is 00:aa:bb:cc:dd:ee and the current time is 01:23 in the morning. A separate file
will be created for each site pinged.

The function measure() can also be called with parameters number_pings, packet_size as well as saveToFile. All of these are optional. The parameter targets is an array of strings describing the sites you want to perform measurements on.

Example usage:
measure(number_pings=30, saveToFile=True, targets = ["www.bbc.com", "www.sics.se"])
This will ping the two sites 30 times and save each ping result to a separate file.
"""

import MySQLdb
import os
import sys
from subprocess import Popen, PIPE, STDOUT
import urllib2
import warnings
import uuid
import socket
import fcntl
import struct
from datetime import datetime
import re

#main measure funtion
def measure(number_pings = 10, packet_size = 64, targets = None, saveToFile=False):
	if targets is None:
		targets = []
	print number_pings, packet_size, targets, saveToFile
	
        database = MySQLdb.connect("localhost", "urban", "basketphone", "buffer")
        curs=database.cursor()

        #To ignore warning from Mysql "Table already existed". Move to setup.py or something? Not exactly important to re-run every run.																																																											
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		sqlTable = """create table if not exists ping(ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                                       	 sourceAddress TEXT, destinationDomain TEXT, destinationAddress TEXT,
							 startingTime DATETIME, endingTime DATETIME, minimumRTT FLOAT,
                                                         averageRTT FLOAT, maximumRTT FLOAT, packetLoss TEXT,
							 ethernetMacAddress TEXT, currentMacAddress TEXT, packetSize INTEGER,
							 numberOfPings INTEGER);"""
                curs.execute(sqlTable)

	ethmac = getEthMAC()
	for target in targets:
		print "target: ", target
		startTime = datetime.now()
		ret = getData(target, number_pings, packet_size)
		endTime = datetime.now()
		
		if saveToFile:
			writeFile(ret, startTime, ethmac)
		readable = reformat(ret, startTime, endTime, ethmac, packet_size, number_pings)
		insertData(database, curs, readable)

	database.close()

	#general logging here? unable to connect etc


#file function
def writeFile(ret, startTime, ethmac):
	fileName = "./" + ethmac+str(startTime) +".txt"
	#print fileName
	myfile = open(fileName, 'w')
	
	myfile.write(ret)
	myfile.close()

#ping function
def getData(destination, packet_number, packet_size):
	print "calling ping"

        execute = "ping -c %s -s %s %s"%(packet_number, packet_size, destination)
	print execute
        result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

	ret = result.stdout.read()
	result.stdout.flush()
	return ret

#read the data from ping and reformat for database entry
def reformat(data, startTime, endTime, ethmac, packet_size, number_pings):
	ret = {}
	ret["startingTime"] = startTime
	ret["endingTime"] = endTime
	ret["ethernetMacAddress"] = ethmac
	ret["packetSize"] = packet_size
	ret["numberOfPings"] = number_pings
	ret["currentMacAddress"] = getCurrMAC() 
	ret["sourceAddress"] = getSA()

	lines = data.split("\n")
	tmp = lines[0].split()
	ret["destinationDomain"] = tmp[1]
	ret["destinationAddress"] = re.sub("[()]", "", str(tmp[2]))
	for line in lines[1:]:
		if "packet loss" in line:
			tmp = line.split()[5]
			ret["packet_loss"] = str(tmp) #INTEGER LATER ON PLEASE ;_;
		if "min/avg/max" in line:
			tmp = line.split()[3].split("/")
			ret["minimumRTT"] = float(tmp[0])
			ret["averageRTT"] = float(tmp[1])
			ret["maximumRTT"] = float(tmp[2])
	
	return ret

#insert the ping results into the database, looks awful, just awful
def insertData(database, cursor, readable):
	
        with database:
                sqlInsert = """INSERT INTO ping (sourceAddress, destinationDomain, destinationAddress,
					        startingTime, endingTime, minimumRTT, averageRTT, maximumRTT, 
						packetLoss, ethernetMacAddress, currentMacAddress, packetSize, 
						numberOfPings) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute (sqlInsert,( readable["sourceAddress"], readable["destinationDomain"], readable["destinationAddress"], readable["startingTime"].strftime('%Y-%m-%d %H:%M:%S'), readable["endingTime"].strftime('%Y-%m-%d %H:%M:%S'), readable["minimumRTT"], readable["averageRTT"], readable["maximumRTT"], readable["packet_loss"], readable["ethernetMacAddress"], readable["currentMacAddress"], readable["packetSize"], readable["numberOfPings"]))

                database.commit()

#get the ethernet mac address of this device
def getEthMAC(ifname = "eth0"):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

#get our currently used MAC address
def getCurrMAC():
	ret =':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
	return ret
	
#get our source address
def getSA():
	ret = urllib2.urlopen('http://ip.42.pl/raw').read()
	return ret

#parses arguments
if __name__ == "__main__":
	#if len(sys.argv) < 3:
	#	print "too few parameters"
	#	sys.exit(1)

	args = (sys.argv)
	args = args[1:]
	
	number = 10
	size = 64
	destinations = []
	save = False

	#should make this check better, could easily have a problem with some websites	
	for arg in args:
		if "-number=" in arg:
			number = arg.split("=")[1]
		elif "-size=" in arg:
			size = arg.split("=")[1]
		elif "-save=" in arg:
			print "save!"
			save = (arg.split("=")[1] in ['True', 'true'])
		else:
			destinations.append(str(arg))
	
	measure(number_pings = number, packet_size = size, targets = destinations, saveToFile=save)



