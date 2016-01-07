import time
import os
import re
import logging
import socket
from subprocess import Popen, PIPE

import Task
import cheesepilib as cp
logger = cp.config.get_logger()

class Httping(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.spec['taskname'] = "httping"
		if not 'landmark'    in self.spec: self.spec['landmark']    = "google.com"
		if not 'ping_count'  in self.spec: self.spec['ping_count']  = 10
		try:
			socket.gethostbyname(self.spec['landmark']) # we dont care, just populate the cache
		except:
			pass # record network failure later...

	def toDict(self):
		return self.spec

	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("HTTPinging: %s @ %f, PID: %d" % (self.spec['landmark'], time.time(), os.getpid()))
		self.measure(self.spec['landmark'], self.spec['ping_count'])


	#main measure funtion
	def measure(self, landmark, ping_count):
		start_time = cp.utils.now()
		op_output = self.perform(landmark, ping_count)
		end_time = cp.utils.now()
		logger.debug(op_output)

		parsed_output = self.parse_output(op_output, landmark, start_time, end_time, ping_count)
		self.dao.write_op("httping", parsed_output)

	#ping function
	def perform(self, landmark, ping_count):
		execute = "httping -S -c %s %s" % (ping_count, landmark)
		logging.info("Executing: "+execute)
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	# average out the breakdowns if different steps in HTTP request
	def parse_breakdowns(self, breakdowns):
		acc=[0.0] * len(breakdowns[0])
		for i in xrange(len(breakdowns)):
			for j in xrange(len(breakdowns[i])):
				acc[j] += float(breakdowns[i][j])
		return [x / len(breakdowns) for x in acc]

	#read the data from ping and reformat for database entry
	def parse_output(self, data, landmark, start_time, end_time, ping_count):
		ret = {}
		ret["landmark"]    = landmark
		ret["start_time"]  = start_time
		ret["end_time"]    = end_time
		ret["ping_count"]  = int(ping_count)
		delays=[]
		breakdowns=[]

		lines = data.split("\n")
		first_line = lines.pop(0).split()
		ret["destination_domain"]  = first_line[1]

		delays = [-1.0] * ping_count# initialise storage
		for line in lines:
			if "time=" in line: # is this a PING return line?
				# does the following string wrangling always hold? what if not "X ms" ?
				# also need to check whether we are on linux-like or BSD-like ping
				sequence_num = int(re.findall('seq=[\d]+ ',line)[0][4:-1])

				delay = re.findall('[\d\.]+ ms',line)[0][0:-3]
				# only save returned pings!
				delays[sequence_num]=float(delay)

				# capture split breakdown of httping
				splits = re.findall('time=.*=',line)[0][5:-1]
				breakdowns.append(splits.split("+"))

			if "packet loss" in line:
				loss = re.findall('[\d]+% packet loss',line)[0][:-13]
				ret["packet_loss"] = float(loss)
			elif "min/avg/max" in line:
				fields = line.split()[3].split("/")
				ret["minimum_RTT"] = float(fields[0])
				ret["average_RTT"] = float(fields[1])
				ret["maximum_RTT"] = float(fields[2])
		ret['delays'] = str(delays)
		ret["stddev_RTT"]  = cp.utils.stdev(delays)
		ret['breakdown'] = str(self.parse_breakdowns(breakdowns))
		return ret


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao    = cp.config.get_dao()
	config = cp.config.get_config()

	spec = {'landmark':'google.com'}
	httping_task = Httping(dao, spec)
	httping_task.run()




