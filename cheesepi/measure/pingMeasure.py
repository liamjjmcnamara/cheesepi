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
Re-written by: ljjm@sics.se
Testers:

Example usage:
$ python pingMeasure.py

This will ping each of the 'landmarks' from the cheesepi.conf.
"""

import sys
from subprocess import Popen, PIPE
import re
import logging

# try to import cheesepi, i.e. it's on PYTHONPATH
sys.path.append("/usr/local/")
import cheesepi

#main measure funtion
def measure(dao, landmarks, ping_count, packet_size, save_file=False):
	for landmark in landmarks:
		start_time = cheesepi.utils.now()
		op_output = perform(landmark, ping_count, packet_size)
		end_time = cheesepi.utils.now()
		#print op_output

		parsed_output = parse_output(op_output, start_time, end_time, packet_size, ping_count)
		if save_file: # should we save the whole output?
			dao.write_op("ping", parsed_output, op_output)
		else:
			dao.write_op("ping", parsed_output)

#ping function
def perform(destination, ping_count, packet_size):
	packet_size -= 8 # change packet size to payload length!
	execute = "ping -c %s -s %s %s"%(ping_count, packet_size, destination)
	logging.info("Executing: "+execute)
	print execute
	result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
	ret = result.stdout.read()
	result.stdout.flush()
	return ret

#read the data from ping and reformat for database entry
def parse_output(data, start_time, end_time, packet_size, ping_count):
	ret = {}
	ret["start_time"]  = start_time
	ret["end_time"]    = end_time
	ret["packet_size"] = int(packet_size)
	ret["ping_count"]  = int(ping_count)
	delays=[]

	lines = data.split("\n")
	first_line = lines.pop(0).split()
	ret["destination_domain"]  = first_line[1]
	ret["destination_address"] = re.sub("[()]", "", str(first_line[2]))

	delays = [-1.0] * ping_count# initialise storage
	for line in lines:
		if "time=" in line: # is this a PING return line?
			# does the following string wrangling always hold? what if not "X ms" ?
			# also need to check whether we are on linux-like or BSD-like ping
			if "icmp_req" in line: # BSD counts from 1
				sequence_num = int(re.findall('icmp_.eq=[\d]+ ',line)[0][9:-1]) -1
			elif "icmp_seq" in line: # Linux counts from 0
				sequence_num = int(re.findall('icmp_.eq=[\d]+ ',line)[0][9:-1])
			else:
				logging.error("ping parse error:"+line)
				exit(1)
			delay = re.findall('time=.*? ms',line)[0][5:-3]
			#print sequence_num,delay
			# only save returned pings!
			delays[sequence_num]=float(delay)
	ret['delays'] = str(delays)

	# probably should not reiterate over lines...
	for line in lines:
		if "packet loss" in line:
			loss = re.findall('[\d]+% packet loss',line)[0][:-13]
			ret["packet_loss"] = float(loss)
		elif "min/avg/max/" in line:
			fields = line.split()[3].split("/")
			ret["minimum_RTT"] = float(fields[0])
			ret["average_RTT"] = float(fields[1])
			ret["maximum_RTT"] = float(fields[2])
			ret["stddev_RTT"]  = float(fields[3])
	return ret


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()
	config = cheesepi.config.get_config()

	landmarks = cheesepi.config.get_landmarks()

	ping_count = 10
	if cheesepi.config.config_defined("ping_count"):
		ping_count = int(cheesepi.config.get("ping_count"))

	packet_size = 64 # this is total packet size, not contents! (check ping man page)
	if cheesepi.config.config_defined("ping_packet_size"):
		packet_size= int(cheesepi.config.get("ping_packet_size"))

	save_file = cheesepi.config.config_equal("ping_save_file","true")

	print "Landmarks: ",landmarks
	measure(dao, landmarks, ping_count, packet_size, save_file)

