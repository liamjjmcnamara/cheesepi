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

import sys
from subprocess import Popen, PIPE
import re

# try to import cheesepi, i.e. it's on PYTHONPATH
try:
    import cheesepi
except:
    # try default location
    sys.path.append("/usr/local/")
    import cheesepi

#main measure funtion
def measure(dao, number_httpings = 10, targets = None, save_file=False):
	if targets is None:
		return

	ethmac = cheesepi.utils.get_MAC()
	for target in targets:
		start_time    = cheesepi.utils.now()
		httpingResult = getData(target, number_httpings)
		end_time      = cheesepi.utils.now()
		if save_file:
			cheesepi.utils.write_file(httpingResult, start_time, ethmac)
		readable = reformat(httpingResult, start_time, end_time, ethmac, number_httpings)
		print readable
		dao.write_op("httping",readable)


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
def reformat(data, start_time, end_time, ethmac, number_httpings):
	ret = {}
	ret["start_time"] = start_time
	ret["end_time"]   = end_time
	ret["numberOfHttpings"] = int(number_httpings)
#print "numberOfHttpings = %s" % ret["numberOfHttpings"]
	ret["ethernet_MAC"]   = ethmac
	ret["current_MAC"]    = cheesepi.utils.get_MAC()
	ret["source_address"] = cheesepi.utils.get_SA()

	lines = data.split("\n")
	tmp = lines[0].split()
	ret["destination_domain"] = re.sub("[:80]", "", str(tmp[1]))

	for line in lines[1:]:
		if "bytes)," in line:
			tmp = line.split()
			ret["destination_address"] = re.sub("[:80]", "", str(tmp[2]))
			ret["packet_size"] = int(re.sub("[(bytes),]", "", str(tmp[3])))
			#print "Packet size = %s" %ret["packetSize"]
			if "% failed" in line:
					tmp = line.split()[4]
					ret["packet_loss"] = str(tmp)[:-1]
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

	measure(dao, number_httpings=number, targets=destinations, save_file=save)

