import sys
import time
import os
import re
import logging
import socket
from subprocess import Popen, PIPE

sys.path.append("/usr/local/")
import Task
import cheesepi.utils

class Httping(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname	 = "httping"
		self.landmark	 = parameters['landmark']
		self.ping_count  = 10 #parameters['ping_count']
		self.packet_size = 64 #parameters['packet_size']
		socket.gethostbyname(self.landmark) # we dont care, just populate the cache

	def toDict(self):
		return {'taskname'	 :self.taskname,
				'landmark'	 :self.landmark,
				'ping_count' :self.ping_count,
				}

	# actually perform the measurements, no arguments required
	def run(self):
		print "HTTPinging: %s @ %f, PID: %d" % (self.landmark, time.time(), os.getpid())
		self.measure(self.landmark, self.ping_count)


	#main measure funtion
	def measure(self, landmark, ping_count):
		start_time = cheesepi.utils.now()
		op_output = self.perform(landmark, ping_count)
		end_time = cheesepi.utils.now()
		print op_output

		parsed_output = self.parse_output(op_output, landmark, start_time, end_time, ping_count)
		self.dao.write_op("httping", parsed_output)

	#ping function
	def perform(self, landmark, ping_count):
		execute = "httping -c %s %s" % (ping_count, landmark)
		print execute
		logging.info("Executing: "+execute)
		#print execute
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	#read the data from ping and reformat for database entry
	def parse_output(self, data, landmark, start_time, end_time, ping_count):
		ret = {}
		ret["landmark"]    = landmark
		ret["start_time"]  = start_time
		ret["end_time"]    = end_time
		ret["ping_count"]  = int(ping_count)
		delays=[]

		lines = data.split("\n")
		first_line = lines.pop(0).split()
		ret["destination_domain"]  = first_line[1]

		delays = [-1.0] * ping_count# initialise storage
		for line in lines:
			if "time=" in line: # is this a PING return line?
				# does the following string wrangling always hold? what if not "X ms" ?
				# also need to check whether we are on linux-like or BSD-like ping
				sequence_num = int(re.findall('seq=[\d]+ ',line)[0][4:-1])
				delay = re.findall('time=.*? ms',line)[0][5:-3]
				# only save returned pings!
				delays[sequence_num]=float(delay)
		ret['delays'] = str(delays)
		ret["stddev_RTT"]  = cheesepi.utils.stdev(delays)

		# probably should not reiterate over lines...
		for line in lines:
			if "packet loss" in line:
				loss = re.findall('[\d]+% packet loss',line)[0][:-13]
				ret["packet_loss"] = float(loss)
			elif "min/avg/max" in line:
				fields = line.split()[3].split("/")
				ret["minimum_RTT"] = float(fields[0])
				ret["average_RTT"] = float(fields[1])
				ret["maximum_RTT"] = float(fields[2])
		return ret


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()
	config = cheesepi.config.get_config()

	landmarks = cheesepi.config.get_landmarks()

	ping_count = 10
	if cheesepi.config.config_defined("httping_count"):
		ping_count = int(cheesepi.config.get("httping_count"))


	print "Landmarks: ",landmarks

	parameters = {'landmark':'google.com'}
	httping_task = Httping(dao, parameters)
	httping_task.run()




