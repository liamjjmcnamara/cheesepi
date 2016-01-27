import time
import os
import re
import logging
import socket

import Task
import cheesepi as cp

logger = cp.config.get_logger(__name__)

class Httping(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.spec['taskname'] = "httping"
		if not 'landmark'    in self.spec: self.spec['landmark']    = "www.sics.se"
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
		if op_output!=None:
			self.parse_output(op_output, landmark, start_time, end_time, ping_count)
		self.dao.write_op("httping", self.spec)

	#ping function
	def perform(self, landmark, ping_count):
		command = "httping -S -c %s %s" % (ping_count, landmark)
		logging.info("Executing: "+command)
		self.spec['return_code'], output = self.execute(command)
		#print self.spec['return_code'], output
		if self.spec['return_code']==0:
			return output
		return None

	# average out the breakdowns if different steps in HTTP request
	def parse_breakdowns(self, breakdowns):
		acc=[0.0] * len(breakdowns[0])
		for i in xrange(len(breakdowns)):
			for j in xrange(len(breakdowns[i])):
				acc[j] += float(breakdowns[i][j])
		return [x / len(breakdowns) for x in acc]

	#read the data from ping and reformat for database entry
	def parse_output(self, data, landmark, start_time, end_time, ping_count):
		self.spec["landmark"]    = landmark
		self.spec["start_time"]  = start_time
		self.spec["end_time"]    = end_time
		self.spec["ping_count"]  = int(ping_count)
		delays=[]
		breakdowns=[]
		downloaded = 0 # how many bytes delivered?

		lines = data.split("\n")
		first_line = lines.pop(0).split()
		self.spec["destination_domain"]  = first_line[1]

		delays = [-1.0] * ping_count# initialise storage
		for line in lines:
			if "time=" in line: # is this a PING return line?
				# does the following string wrangling always hold? what if not "X ms" ?
				# also need to check whether we are on linux-like or BSD-like ping
				downloaded  += int(re.findall('[\d]+ bytes',line)[0][:-6])
				sequence_num = int(re.findall('seq=[\d]+ ',line)[0][4:-1])

				delay = re.findall('[\d\.]+ ms',line)[0][0:-3]
				# only save returned pings!
				delays[sequence_num]=float(delay)

				# capture split breakdown of httping
				splits = re.findall('time=.*=',line)[0][5:-1]
				breakdowns.append(splits.split("+"))

			if "packet loss" in line:
				loss = re.findall('[\d]+% packet loss',line)[0][:-13]
				self.spec["packet_loss"] = float(loss)
			elif "min/avg/max" in line:
				fields = line.split()[3].split("/")
				self.spec["minimum_RTT"] = float(fields[0])
				self.spec["average_RTT"] = float(fields[1])
				self.spec["maximum_RTT"] = float(fields[2])
		self.spec['delays']     = str(delays)
		self.spec["stddev_RTT"] = cp.utils.stdev(delays)
		self.spec['breakdown']  = str(self.parse_breakdowns(breakdowns))
		self.spec['downloaded'] = downloaded


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao    = cp.config.get_dao()
	config = cp.config.get_config()

	spec = {'landmark':'www.sics.se'}
	httping_task = Httping(dao, spec)
	httping_task.run()




