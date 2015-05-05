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
import sys
from subprocess import Popen, PIPE
import re
import copy

# try to import cheesepi, i.e. it's on PYTHONPATH
sys.path.append("/usr/local/")
import cheesepi


def measure(dao, landmarks, saveToFile=False):
	trc = Traceroute()
	hoplist = []
	#Extract the ethernet MAC address of the PI
	for landmark in landmarks:
		startTime = cheesepi.utils.now()
		tracerouteResult = getData(landmark)
		endTime = cheesepi.utils.now()
		trc, hoplist = reformat(tracerouteResult, startTime, endTime)
		insertData(dao, trc, hoplist)

#Execute traceroute function
def getData(target):
	#traceroute command"
	execute = "traceroute %s"%(target)
	#Executing the above shell command with pipe
	result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	ret = result.stdout.read()
	result.stdout.flush()
	return ret

#A Traceroute class to represent the Traceroute table
class Traceroute(object):
	StartingTime = None
	EndingTime = None
	SourceAddress = None
	DestinationDomain = None
	DestinationAddress = None

#A Hop class to represent the Hop table
class Hop(object):
	_id = None
	HopNumber = None
	PacketNumber = None
	PacketDestinationAddress = None
	PacketDestinationDomain = None
	RTT = None


#########################
## Mac traceroute
########################
def parse_mac(data):
	hops=[]
	lines = data.split()
	lines.pop(0)
	hop_count=-1
	while (len(lines)>0):
		line = lines.pop(0)
		hop_count = int(line[:3].strip())
		print hop_count
		host_line = line[4:] # extract everything after hopcount
		host_fields = host_line.split()
		if len(host_fields)==3:
			hops.extend(parse_null(hop_count))
		elif len(host_fields)==8: # the same host responds for each retry
			hop_entries = parse_hop_1host(hop_count,host_fields)
			hops.extend(hop_entries)
		elif len(host_fields)==4: # multiple hosts respond at this hop
			retry2 = lines.pop(0)[4:] #pop the next 2 lines
			retry3 = lines.pop(0)[4:]
			hop_entries = parse_hop_3host(hop_count,host_line, retry2, retry3)
			hops.extend(hop_entries)
	print hops
	return hops

def parse_null(hop_count):
	return {'hop_count': hop_count,
		'domain1': "*", 'domain2': "*", 'domain3': "*",
		'ip1'    : "*", 'ip2'    : "*", 'ip3'    : "*",
		'delay1': -1, 'delay2': -1, 'delay3': -1, }

def parse_hop_1host(hop_count, host_fields):
	return {'hop_count': hop_count,
		'domain1': host_fields[0],
		'domain2': host_fields[0],
		'domain3': host_fields[0],
		'ip1'    : host_fields[1],
		'ip2'    : host_fields[1],
		'ip3'    : host_fields[1],
		'delay1': host_fields[2],
		'delay2': host_fields[4],
		'delay3': host_fields[6],
		}

def parse_hop_3host(hop_count, retry1, retry2, retry3):
	retry1_fields = retry1.split()
	retry2_fields = retry2.split()
	retry3_fields = retry3.split()
	return {'hop_count': hop_count,
		'domain1': retry1_fields[0],
		'domain2': retry1_fields[0],
		'domain3': retry1_fields[0],
		'ip1'   : retry1_fields[1],
		'ip2'   : retry2_fields[1],
		'ip3'   : retry3_fields[1],
		'delay1': retry1_fields[2],
		'delay2': retry2_fields[2],
		'delay3': retry3_fields[2],
		}

#############################

def parse(data):
	hops=[]
	lines = data.split()
	for line in lines[1:]:
		hop_count   = int(line[:3].strip())
		host_line   = line[4:] # extract everything after hopcount
		host_fields = host_line.split()
		if len(host_fields)==3:
			hops.extend(parse_null(hop_count))
		else:
			hop_entries = parse_hop(hop_count, host_fields)
			hops.extend(hop_entries)
	print hops
	return hops

def parse_hop(hop_count, host_fields):
	if   len(host_fields)==8:
		return {'hop_count': hop_count,
			'domain1':host_fields[0],       'domain2':host_fields[0],        'domain3':host_fields[0],
			'ip1'    :host_fields[1][1:-1], 'ip2'    :host_fields[1][1:-1],  'ip3'    :host_fields[1][1:-1],
			'delay1' :float(host_fields[2]),'delay2' :float(host_fields[4]), 'delay3' :float(host_fields[6]),
			}
	elif len(host_fields)==11:
		return {'hop_count': hop_count,
			'domain1':host_fields[0],       'domain2':host_fields[4],       'domain3':host_fields[8],
			'ip1'    :host_fields[1][1:-1], 'ip2'    :host_fields[5][1:-1], 'ip3'    :host_fields[9][1:-1],
			'delay1' :float(host_fields[2]),'delay2' :float(host_fields[6]),'delay3' :float(host_fields[10]),
			}
	else:
		print "Error parsing host line: "+str(host_fields)
		exit(1)


#read the data from traceroute and reformat for database entry
def reformat(data, startTime, endTime):
	trc = Traceroute()
	#hop = Hop()
	hoplist = []
	print "Structuring the traceroute result"
	trc.StartingTime = startTime
	trc.EndingTime = endTime
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


#insert the tracetoute results into the database
def insertData(dao, trc, hoplist):
	#insertIntoTraceroute = """INSERT INTO Traceroute(sourceAddress, destinationDomain, destinationAddress,
	#	startingTime, endingTime, ethernetMacAddress, currentMacAddress)
	#	values (%s,%s,%s,%s,%s,%s,%s)"""
	#insertIntoHop = """INSERT INTO Hop(ID, hopNumber, packetNumber, packetDomainAddress, packetDestinationAddress,
	#	RTT) values (%s,%s,%s,%s,%s,%s)"""

	print "Writting to the Traceroute tabele"
	traceroute_id = dao.write_op("traceroute", trc.as_dict())

	print "writing to the Hop table"
	for hop in hoplist:
		hop.traceroute = traceroute_id
		dao.write_op("traceroot_hop",hop.as_dict())


#parses arguments
if __name__ == "__main__":
	#general logging here? unable to connect etc
	config = cheesepi.config.get_config()
	dao = cheesepi.config.get_dao()

	landmarks = cheesepi.config.get_landmarks()
	save_file = cheesepi.config.config_equal("ping_save_file","true")

	print "Landmarks: ",landmarks
	measure(dao, landmarks, save_file)
	dao.close()


