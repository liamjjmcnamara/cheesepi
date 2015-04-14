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

import sys
from subprocess import Popen, PIPE
import re
import logging

import cheesepi

#main measure funtion
def measure(dao, number_pings=10, packet_size=64, targets=None, save_file=False):
	if targets is None:
		return

	ethmac = cheesepi.utils.get_MAC()
	for target in targets:
		print target
		start_time = cheesepi.utils.now()
		op_output = perform(target, number_pings, packet_size)
		end_time = cheesepi.utils.now()

		if save_file:
			cheesepi.utils.write_file(op_output, start_time, ethmac)
		parsed_output = parse_output(op_output, start_time, end_time, ethmac, packet_size, number_pings)
		dao.write_op("ping", parsed_output)

#ping function
def perform(destination, packet_number, packet_size):
	#print "calling ping"

	execute = "ping -c %s -s %s %s"%(packet_number, packet_size, destination)
	logging.error("Executing: "+execute)
	#print execute
	result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

	ret = result.stdout.read()
	result.stdout.flush()
	return ret

#read the data from ping and reformat for database entry
def parse_output(data, start_time, end_time, ethmac, packet_size, number_pings):
	ret = {}
	ret["start_time"]    = start_time
	ret["ending_time"]   = end_time
	ret["packet_size"]   = int(packet_size)
	ret["ping_count"]    = int(number_pings)
	ret["ethernet_MAC"]  = ethmac
	ret["current_MAC"]   = cheesepi.utils.get_MAC()
	ret["source_address"]= cheesepi.utils.get_SA()

	lines = data.split("\n")
	tmp = lines[0].split()
	ret["destination_domain"] = tmp[1]
	ret["destination_address"] = re.sub("[()]", "", str(tmp[2]))
	for line in lines[1:]:
		if "packet loss" in line:
			tmp = line.split()[5]
			ret["packet_loss"] = str(tmp) #INTEGER LATER ON PLEASE ;_;
		if "min/avg/max" in line:
			tmp = line.split()[3].split("/")
			ret["minimum_RTT"] = float(tmp[0])
			ret["average_RTT"] = float(tmp[1])
			ret["maximum_RTT"] = float(tmp[2])

	return ret


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

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

	measure(dao, number_pings=number, packet_size=size, targets=destinations, save_file=save)

