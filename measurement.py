#!/usr/bin/python 

import MySQLdb
import os
import sys
from subprocess import Popen, PIPE, STDOUT
import urllib2
import warnings

#Global variables
minRTT = 0.0
avgRTT = 0.0
maxRTT = 0.0
packetLoss = None
desAddr = ''
db = None
curs = None
sourceAddr = urllib2.urlopen('http://ip.42.pl/raw').read()

def main():
	global db
	global curs
	db = MySQLdb.connect("localhost", "measurement", "MP4MDb", "Measurement")
	curs=db.cursor()
	sqlTable = """create table if not exists ping(ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
							 sourceAddress TEXT, destinationAddress TEXT, minimumRTT FLOAT,
    							 averageRTT FLOAT, maximumRTT FLOAT, packetLoss TEXT);"""
	#To ignore warning from Mysql "Table already existed"
	with warnings.catch_warnings():
		warnings.simplefilter("ignore") 
		curs.execute(sqlTable)
	pingDestination("bbc.com")
	pingDestination("diretube.com")
	pingDestination("sics.se")
	db.close()

#ping function
def pingDestination(destination):
	global minRTT
	global avgRTT
	global maxRTT
	global desAddr
	global packetLoss

	
	ping = "ping -c  10 %s"%destination
	p = Popen(ping ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	line = p.stdout.readline()
	while True:
	        if 'PING' in line:
	                destination = line.split(' ')
	                desAddr = str(destination[1])+str(destination[2])
		if 'packets' in line:
                        packets = line.split(' ')
                        packetLoss = str(packets[5])

	        if '/' in line:
	                rttData = line.split('/')
	                rttData2 = rttData[3].split(' = ')
	                minRTT = float(rttData2[1])
	                avgRTT = float(rttData[4])
	                maxRTT = float(rttData[5])
	                break
		
	        if line == "":
	                break
        	line = p.stdout.readline()
	p.stdout.flush() 
	insertToTable()
def insertToTable():
	global db
	global curs
	global minRTT
	global avgRTT
	global maxRTT
	global sourceAddr
	global desAddr
	global packetLoss
	with db:
    	    	sqlInsert = "INSERT INTO ping(sourceAddress, destinationAddress, minimumRTT, averageRTT, maximumRTT, packetLoss) values(%s,%s,%s,%s,%s,%s)"
    		curs.execute (sqlInsert,( sourceAddr, desAddr, minRTT, avgRTT,maxRTT, packetLoss))
    		db.commit()
    		print "Data Submitted successfully "


if __name__ == "__main__":
    main()

