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

Authors: guulay@kth.se
Testers:

Example usage:
python httpingMeasure.py -save=False -number=10 www.bbc. com www.sics.se www.diretube.com

This is equal to:
httping -c 10 www.bbc.com
httping -c 10 www.sics.se
httping -c 10 www.svt.se

and do not save the resuls in file


If -save=True the program will attempt to write the the result of 
each http in a separate file named after the device's 
ethernet mac address + the current date. 
For example 00:aa:bb:cc:dd:ee 20-2015-14:00:01.txt

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
def measure(number_httpings = 10, targets = None, saveToFile=False):
        if targets is None:
                targets = []
        
        database = MySQLdb.connect("localhost", "measurement", "MP4MDb", "Measurement")
        curs=database.cursor()

        #To ignore warning from Mysql "Table already existed".        
        with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sqlTable = """create table if not exists httping(ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                                         sourceAddress TEXT, destinationDomain TEXT, destinationAddress TEXT,
                                                         startingTime DATETIME, endingTime DATETIME, minimumRTT FLOAT,
                                                         averageRTT FLOAT, maximumRTT FLOAT, packetLoss TEXT,
                                                         ethernetMacAddress TEXT, currentMacAddress TEXT, packetSize INTEGER,
                                                         numberOfHttpings INTEGER);"""
                curs.execute(sqlTable)

        ethmac = getEthMAC()
        for target in targets:
                startTime = datetime.now()
                httpingResult = getData(target, number_httpings)
                endTime = datetime.now()
                if saveToFile:
                        writeFile(httpingResult, startTime, ethmac)
                readable = reformat(httpingResult, startTime, endTime, ethmac, number_httpings)
		insertData(database, curs, readable)

        database.close()

        #general logging here? unable to connect etc


#Writing httping results to file function
def writeFile(httpingResult, startTime, ethmac):
        fileName = "./" + ethmac+str(startTime) +".txt"
        #print fileName
        myfile = open(fileName, 'w')

        myfile.write(httpingResult)
        myfile.close()

#Execute httping function
def getData(destination, packet_number):
        #httping command"

        execute = "httping -c %s %s"%(packet_number, destination)
        #Executing the above shell command in with pipe
        result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	#Read the data from the pipe
        ret = result.stdout.read()
        result.stdout.flush()
        return ret
#read the data from httping and reformat for database entry
def reformat(data, startTime, endTime, ethmac, number_httpings):
        ret = {}
        ret["startingTime"] = startTime
        ret["endingTime"] = endTime
        ret["ethernetMacAddress"] = ethmac
        ret["numberOfHttpings"] = number_httpings
	#print "numberOfHttpings = %s" % ret["numberOfHttpings"]
        ret["currentMacAddress"] = getCurrMAC()
        ret["sourceAddress"] = getSA()

        lines = data.split("\n")
        tmp = lines[0].split()
        ret["destinationDomain"] = re.sub("[:80]", "", str(tmp[1]))
	       
        for line in lines[1:]:
		
		if "bytes)," in line:
			tmp = line.split()
			ret["destinationAddress"] = re.sub("[:80]", "", str(tmp[2]))
	  		ret["packetSize"] = int(re.sub("[(bytes),]", "", str(tmp[3])))
			#print "Packet size = %s" %ret["packetSize"]
                if "% failed" in line:
                        tmp = line.split()[4]
                        ret["packet_loss"] = str(tmp)
                if "min/avg/max" in line:
                        tmp = line.split()[3].split("/")
                        ret["minimumRTT"] = float(tmp[0])
                        ret["averageRTT"] = float(tmp[1])
                        ret["maximumRTT"] = float(tmp[2])

        return ret

#insert the ping results into the database, looks awful, just awful
def insertData(database, cursor, readable):

        with database:
                sqlInsert = """INSERT INTO httping (sourceAddress, destinationDomain, destinationAddress,
						startingTime, endingTime, minimumRTT, averageRTT, maximumRTT, 
                                                packetLoss, ethernetMacAddress, currentMacAddress, packetSize, 
                                                numberOfHttpings) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute (sqlInsert,( readable["sourceAddress"], readable["destinationDomain"], readable["destinationAddress"], 
					    readable["startingTime"].strftime('%Y-%m-%d %H:%M:%S'), 
                                            readable["endingTime"].strftime('%Y-%m-%d %H:%M:%S'), readable["minimumRTT"],
                                            readable["averageRTT"], readable["maximumRTT"], readable["packet_loss"], 
                                            readable["ethernetMacAddress"], readable["currentMacAddress"], 
                                            readable["packetSize"], readable["numberOfHttpings"]))

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
        #       print "too few parameters"
        #       sys.exit(1)

        args = (sys.argv)
        args = args[1:]
	number = 10
        destinations = []
        save = False

        #should make this check better, could easily have a problem with some websites  
        for arg in args:
                if "-number=" in arg:
                        number = arg.split("=")[1]
			print number
                elif "-save=" in arg:
                        print "save!"
                        save = (arg.split("=")[1] in ['True', 'true'])
                else:
                        destinations.append(str(arg))

        measure(number_httpings = number, targets = destinations, saveToFile=save)

