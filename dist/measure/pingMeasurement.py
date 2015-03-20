#!/usr/bin/python 

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


#Global variables
minRTT = 0.0
avgRTT = 0.0
maxRTT = 0.0
packetLoss = None
desDomain = ''
desAddr = ''
db = None
curs = None
sourceAddr = urllib2.urlopen('http://ip.42.pl/raw').read()
currentMacAddr =  ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
ethernetMacAddr = ''
startTime = None
endTime = None
numberOfPings = 0
packetSize = 0

#main funtion
def main():
        global db
        global curs
	global ethernetMacAddr

	ethernetMacAddr = getEthernetAddr("eth0")
        db = MySQLdb.connect("localhost", "measurement", "MP4MDb", "Measurement")
        curs=db.cursor()
        sqlTable = """create table if not exists ping(ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                                         sourceAddress TEXT, destinationDomain TEXT, destinationAddress TEXT,
							 startingTime DATETIME, endingTime DATETIME, minimumRTT FLOAT,
                                                         averageRTT FLOAT, maximumRTT FLOAT, packetLoss TEXT,
							 ethernetMacAddress TEXT, currentMacAddress TEXT, packetSize INTEGER,
							 numberOfPings INTEGER);"""
        #To ignore warning from Mysql "Table already existed"
        with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                curs.execute(sqlTable)
	#pinging to three different destinations sequentially
        pingDestination("bbc.com")
        pingDestination("diretube.com")
        pingDestination("sics.se")
	db.close()

#A method that returns ethernet address
def getEthernetAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]


#ping function
def pingDestination(destination):
        global minRTT
        global avgRTT
        global maxRTT
	global desDomain
        global desAddr
        global packetLoss
	global startTime
	global endTime
	global numberOfPings
        global packetSize

        ping = "ping -c  10 %s"%destination
	#ping starts at
	startTime = datetime.now()
        p = Popen(ping ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	#Ping ends at
	endTime = datetime.now()
	#Save whole ping results in file for detail information
	fileName = "/home/pi/ping/files/" +str(startTime) +".txt"
	myfile = open(fileName, 'w')
	#Save important parameters from the ping result in the database
        line = p.stdout.readline()
         myfile.write(line)
	while True:
                if 'PING' in line:
                        destinationStr = line.split(' ')
			desDomain = str(destinationStr[1])
                        desAddr = re.sub('[()]', '', str(destinationStr[2]))
		if 'from' in line:
			size = line.split(' ')
			packetSize = int(size[0])
		if 'packets' in line:
                        packets = line.split(' ')
			numberOfPings = int(packets[0])
                        packetLoss = str(packets[5])

                if '/' in line:
                        rttData = line.split('/')
                        rttData2 = rttData[3].split(' = ')
                        minRTT = float(rttData2[1])
                        avgRTT = float(rttData[4])
                        maxRTT = float(rttData[5])
                        break

                line = p.stdout.readline()
		myfile.write(line)
        p.stdout.flush()
	myfile.close()
        insertToTable()

#insert the ping results into the database
def insertToTable():
        global db
        global curs
        global minRTT
        global avgRTT
        global maxRTT
        global sourceAddr
	global desDomain
        global desAddr
	global ethernetMacAddr
	global currentMacAddr
        global packetLoss
	global numberOfPings
        global packetSize
	global startTime
	global endTime
	
	
        with db:
                sqlInsert = """INSERT INTO ping (sourceAddress, destinationDomain, destinationAddress,
					        startingTime, endingTime, minimumRTT, averageRTT, maximumRTT, 
						packetLoss, ethernetMacAddress, currentMacAddress, packetSize, 
						numberOfPings) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                curs.execute (sqlInsert,( sourceAddr, desDomain, desAddr,startTime.strftime('%Y-%m-%d %H:%M:%S'), endTime.strftime('%Y-%m-%d %H:%M:%S'), minRTT, avgRTT,maxRTT, packetLoss, ethernetMacAddr,currentMacAddr, packetSize, numberOfPings))
                db.commit()
                print "Data Submitted successfully "


if __name__ == "__main__":
    main()
