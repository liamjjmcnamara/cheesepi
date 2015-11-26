import sys
import time
import os
import logging
import socket
from subprocess import Popen, PIPE

sys.path.append("/usr/local/")
import cheesepi.utils
import Task

class Status(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters={}):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "status"

	def toDict(self):
		return {'taskname'  :self.taskname,
				}

	# actually perform the measurements, no arguments required
	def run(self):
		print "Status: %s @ %f, PID: %d" % (self.landmark, time.time(), os.getpid())
		self.measure(self.landmark, self.ping_count, self.packet_size)

	#main measure funtion
	def measure(self):
		ethmac = cheesepi.utils.get_MAC()
		start_time = cheesepi.utils.now()
		op_output  = self.perform()
		end_time   = cheesepi.utils.now()

		parsed_output = self.parse_output(op_output, start_time, end_time, ethmac)
		self.dao.write_op("local", parsed_output)

	#ping function
	def perform(self):
		execute = "uptime"
		logging.info("Executing: "+execute)
		#print execute
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)

		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	#read the data from ping and reformat for database entry
	def parse_output(self, data, start_time, end_time, ethmac):
		ret = {}
		ret["start_time"]    = start_time
		ret["end_time"]      = end_time
		ret["ethernet_MAC"]  = ethmac
		ret["current_MAC"]   = cheesepi.utils.get_MAC()
		ret["source_address"]= cheesepi.utils.get_SA()
		# shakey
		ret["local_address"] = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

		fields = data.split()
		ret["uptime"] = fields[2][:-1]
		ret["load1"]  = float(fields[-3][:-1])
		ret["load5"]  = float(fields[-2][:-1])
		ret["load15"] = float(fields[-1])
		return ret


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	status_task = Status(dao)
	status_task.run()
