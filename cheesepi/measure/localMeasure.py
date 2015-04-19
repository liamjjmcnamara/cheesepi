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

Original authors: ljjm@sics.se
Testers:
"""

import sys
from subprocess import Popen, PIPE
import re
import logging

# try to import cheesepi, i.e. it's on PYTHONPATH
sys.path.append("/usr/local/")
import cheesepi

#main measure funtion
def measure(dao, save_file=False):

	ethmac = cheesepi.utils.get_MAC()
	start_time = cheesepi.utils.now()
	op_output = perform()
	end_time = cheesepi.utils.now()

	if save_file:
		cheesepi.utils.write_file(op_output, start_time, ethmac)
	parsed_output = parse_output(op_output, start_time, end_time, ethmac)
	dao.write_op("local", parsed_output)

#ping function
def perform():
	#print "calling ping"

	execute = "uptime"
	logging.info("Executing: "+execute)
	#print execute
	result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

	ret = result.stdout.read()
	result.stdout.flush()
	return ret

#read the data from ping and reformat for database entry
def parse_output(data, start_time, end_time, ethmac):
	ret = {}
	ret["start_time"]    = start_time
	ret["end_time"]   = end_time
	ret["ethernet_MAC"]  = ethmac
	ret["current_MAC"]   = cheesepi.utils.get_MAC()
	ret["source_address"]= cheesepi.utils.get_SA()
	ret["local_address"] = "1.2.3.4"

	fields = data.split()
	ret["uptime"] = fields[2][:-1]
	ret["load1"]  = float(fields[-3][:-1])
	ret["load5"]  = float(fields[-2][:-1])
	ret["load15"] = float(fields[-1])
	return ret


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	measure(dao)

