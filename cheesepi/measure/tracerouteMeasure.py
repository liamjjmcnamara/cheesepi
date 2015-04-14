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
python tracerouteMeasure.py -save=False www.bbc.com www.sics.se www.diretube.com

This is equal to:
traceroute www.bbc.com
traceroute www.sics.se
traceroute www.diretube.com

and do not save the results in a file


If -save=True the program will attempt to write the the result of 
each traceroute in a separate file named after the device's 
ethernet mac address + the current date. 
For example 00:aa:bb:cc:dd:ee 20-2015-14:00:01.txt

"""
import MySQLdb
import os
import sys
from subprocess import Popen, PIPE, STDOUT
import urllib2
import uuid
import socket
import fcntl
import struct
from datetime import datetime
import re
import copy

#A Traceroute class to represent the Traceroute table
class Traceroute(object):
	StartingTime = None
	EndingTime = None
	EthernetMacAddress = None
	CurrentMacAddress = None
	SourceAddress = None
	DestinationDomain = None
	DestinationAddress = None

#A Hop class to represent the Hop table
class Hop(object):
	HopNumber = None
	PacketNumber = None
	PacketDestinationAddress = None
	PacketDestinationDomain = None
	RTT = None

#main measure funtion
def measure(targets = None, saveToFile=False):
	trc = Traceroute()
	#hop = Hop()
	hoplist = []        
	if targets is None:
                targets = []
	database = MySQLdb.connect("localhost", "measurement", "MP4MDb", "Measurement")
        curs=database.cursor()

        #Extract the ethernet MAC address of the PI        
        ethmac = getEthMAC()
        for target in targets:
                startTime = datetime.now()
		print "Traceroute for target started"
                tracerouteResult = getData(target)
                endTime = datetime.now()
		print "Traceroute for target done"
                if saveToFile:
			print "Writing to traceroute results to file"
                        writeFile(tracerouteResult, startTime, ethmac)
                trc, hoplist = reformat(tracerouteResult, startTime, endTime, ethmac)
		insertData(database, curs, trc, hoplist)

        database.close()

        #general logging here? unable to connect etc


#Writing traceroute results to file function
def writeFile(tracerouteResult, startTime, ethmac):
        fileName = "./" + ethmac+str(startTime) +".txt"
        #print fileName
        myfile = open(fileName, 'w')

        myfile.write(tracerouteResult)
        myfile.close()

#Execute traceroute function
def getData(target):
        #traceroute command"
        execute = "traceroute %s"%(target)
        #Executing the above shell command with pipe
        result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	#Read the data from the pipe
        ret = result.stdout.read()
        result.stdout.flush()
        return ret
#read the data from traceroute and reformat for database entry
def reformat(data, startTime, endTime, ethmac):
        trc = Traceroute()
	#hop = Hop()
	hoplist = []
	print "Structuring the traceroute result"
        trc.StartingTime = startTime
        trc.EndingTime = endTime
        trc.EthernetMacAddress = ethmac
        trc.CurrentMacAddress = getCurrMAC()
        trc.SourceAddress = getSA()
	#print data
        lines = data.split("\n")
	tmp = lines[0].split()
        trc.DestinationDomain = str(tmp[2])
	trc.DestinationAddress = re.sub("[(),]", "", str(tmp[3]))
	#print len(lines)     
        for line in lines[1:len(lines)-1]:
		i = 1 # Line length counter
		j = 1 #packet counter
		hop = Hop()
		ip = None
		domain = None
		temp = line.split()
		#print temp[0]
		hop.HopNumber = int(temp[0])
		#till the end of the line
		while i < len(temp):
			#print temp[i]
			if temp[i] == "*":
				hop.PacketNumber = j
				hop.PacketDestinationAddress = None
				hop.PacketDestinationDomain = None
				hop.RTT = -1
				hopcopy = copy.copy(hop)
				hoplist.append(hopcopy)
				i = i + 1
				j = j + 1
                	elif "(" in temp[i+1]:
				hop.PacketNumber = j
				hop.PacketDestinationAddress = re.sub("[(),]", "",str(temp[i+1]))
				hop.PacketDestinationDomain =  str(temp[i])
				hop.RTT = float(temp[i+2])
				hopcopy = copy.copy(hop)
				hoplist.append(hopcopy)
				i = i + 4
                        	j = j + 1

                	elif temp[i+1] == "ms":
				hop.PacketNumber = j
				hop.PacketDestinationAddress = ip
				hop.PacketDestinationDomain = domain
				hop.RTT = float(str(temp[i]))
				hopcopy = copy.copy(hop)
				hoplist.append(hopcopy)
				i = i + 2
				j = j + 1
			ip = hop.PacketDestinationAddress
			domain = hop.PacketDestinationDomain
           
	return trc,hoplist


#get the ethernet mac address of this device
def getEthMAC(ifname = "eth0"):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

#get the currently using MAC address
def getCurrMAC():
        ret =':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        return ret

#get our source address
def getSA():
        ret = urllib2.urlopen('http://ip.42.pl/raw').read()
        return ret

#insert the tracetoute results into the database
def insertData(database, cursor, trc, hoplist):
	print "Inserting the results in to the database"
        with database:
                insertIntoTraceroute = """INSERT INTO Traceroute(sourceAddress, destinationDomain, destinationAddress,
						startingTime, endingTime, ethernetMacAddress, currentMacAddress) 
						values (%s,%s,%s,%s,%s,%s,%s)"""
		insertIntoHop = """INSERT INTO Hop(ID, hopNumber, packetNumber, packetDomainAddress, packetDestinationAddress,
						RTT) values (%s,%s,%s,%s,%s,%s)"""
		print "Writting to the Traceroute tabele"
		cursor.execute(insertIntoTraceroute,(trc.SourceAddress, trc.DestinationDomain, trc.DestinationAddress, 
						      trc.StartingTime.strftime('%Y-%m-%d %H:%M:%S'),
						      trc.EndingTime.strftime('%Y-%m-%d %H:%M:%S'),
						      trc.EthernetMacAddress, trc.CurrentMacAddress))
		#Assigning the traceroute id to the hops  
		lastTracerouteID = "SELECT ID FROM Traceroute ORDER BY ID DESC LIMIT 1"
		cursor.execute(lastTracerouteID)
		id = cursor.fetchone()
		print "writing to the Hop table"
		for hop in hoplist:
			cursor.execute(insertIntoHop, (id[0], hop.HopNumber, hop.PacketNumber, hop.PacketDestinationDomain,
						       hop.PacketDestinationAddress, hop.RTT))
 

                database.commit()


#parses arguments
if __name__ == "__main__":
        
	args = (sys.argv)
        args = args[1:]
	destinations = []
        save = False

        for arg in args:
                
                if "-save=" in arg:
                        print "save!"
                        save = (arg.split("=")[1] in ['True', 'true'])
                else:
                        destinations.append(str(arg))

        measure(targets = destinations, saveToFile=save)

