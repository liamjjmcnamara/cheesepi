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
import platform

# try to import cheesepi, i.e. it's on PYTHONPATH
sys.path.append("/usr/local/")
import cheesepi


def measure(dao, landmarks, saveToFile=False):
	hoplist = []
	#Extract the ethernet MAC address of the PI
	for landmark in landmarks:
		startTime = cheesepi.utils.now()
		output = getData(landmark)
		endTime = cheesepi.utils.now()
		#trc, hoplist = reformat(tracerouteResult, startTime, endTime)
		traceroute, hoplist = parse(output, startTime, endTime)
		insertData(dao, traceroute, hoplist)

#Execute traceroute function
def getData(target):
	#traceroute command"
	execute = "traceroute %s"%(target)
	#Executing the above shell command with pipe
	result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	ret = result.stdout.read()
	result.stdout.flush()
	return ret


def parse_null(hop_count):
	return {'hop_count': hop_count,
		'domain1': "*", 'domain2': "*", 'domain3': "*",
		'ip1'    : "*", 'ip2'    : "*", 'ip3'    : "*",
		'delay1': -1, 'delay2': -1, 'delay3': -1, }

#############################
# Parse Linux command
#

def parse(data, start_time, end_time):
	lines = data.split("\n")
	traceroute = parse_destination(lines[0], start_time, end_time)
	hops=[]
	for line in lines[1:-1]:
		hop_count = int(line[:3].strip())
		hops.append(parse_hop(hop_count, line[4:]))
	print "hops: ",hops
	return traceroute, hops

def parse_destination(destination, start_time, end_time):
	traceroute = {}
	fields = destination.split()
	traceroute['domain']     = fields[2]
	traceroute['ip']         = fields[3][1:-1]
	traceroute['start_time'] = start_time
	traceroute['end_time']   = end_time
	return traceroute

def parse_hop(hop_count, host_line):
	"""This does not yet deal with network problems"""
	hop={'hop_count':hop_count}
	retry="1" # string accumulator
	for match in re.finditer(r"\*|(([\w\.-]+) \(([\d\.]+)\)  ([\d\.ms ]+) )", host_line):
		if match.group(0)=="*": # found a non response
			hop['domain'+retry]="*"
			hop['ip'+retry]="*"
			hop['delay'+retry]="-1"
		else: # some host reploiued N times
			for delay in match.group(4).split("ms"):
				hop['domain'+retry]= match.group(2)
				hop['ip'+retry]    = match.group(3)
				hop['delay'+retry] = delay
				retry = str(int(retry)+1) # inc but keep as string
		retry = str(int(retry)+1) # inc but keep as string
	return hop


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


def parse_hop_1host(hop_count, host_fields):
	return {'hop_count': hop_count,
		'domain1': host_fields[0], 'domain2': host_fields[0], 'domain3': host_fields[0],
		'ip1'    : host_fields[1], 'ip2'    : host_fields[1], 'ip3'    : host_fields[1],
		'delay1': host_fields[2], 'delay2': host_fields[4], 'delay3': host_fields[6],
		}

def parse_hop_3host(hop_count, retry1, retry2, retry3):
	retry1_fields = retry1.split()
	retry2_fields = retry2.split()
	retry3_fields = retry3.split()
	return {'hop_count': hop_count,
		'domain1': retry1_fields[0], 'domain2': retry1_fields[0], 'domain3': retry1_fields[0],
		'ip1'   : retry1_fields[1], 'ip2'   : retry2_fields[1], 'ip3'   : retry3_fields[1],
		'delay1': retry1_fields[2], 'delay2': retry2_fields[2], 'delay3': retry3_fields[2],
		}
###


#insert the tracetoute results into the database
def insertData(dao, traceroute, hoplist):
	print "Writting to the Traceroute tabele"
	traceroute_id = dao.write_op("traceroute", traceroute)

	print "writing to the Hop table"
	for hop in hoplist:
		print hop
		#hop.traceroute = traceroute_id
		hop['traceroute_id'] = traceroute_id
		dao.write_op("traceroot_hop",hop)


#parses arguments
if __name__ == "__main__":
	if platform.system()=="Darwin":
		exit(0)

	#general logging here? unable to connect etc
	config = cheesepi.config.get_config()
	dao = cheesepi.config.get_dao()

	landmarks = cheesepi.config.get_landmarks()
	save_file = cheesepi.config.config_equal("ping_save_file","true")

	print "Landmarks: ",landmarks
	measure(dao, landmarks, save_file)
	dao.close()


