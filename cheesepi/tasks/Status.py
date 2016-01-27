import time
import os
import uptime
import logging
import socket
from subprocess import Popen, PIPE

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

class Status(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec={}):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "status"
		self.spec['downloaded'] = 0
		self.spec['uploaded']   = 0

	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("Status @ %f, PID: %d" % (time.time(), os.getpid()))
		self.measure()

	#main measure funtion
	def measure(self):
		ethmac = cp.utils.get_MAC()
		self.spec['start_time'] = cp.utils.now()
		op_output  = self.measure_uptime()
		self.measure_storage()
		self.measure_temperature()
		parsed_output = self.parse_output(op_output, ethmac)
		self.dao.write_op("status", parsed_output)

	def measure_uptime(self):
		execute = "uptime"
		logging.info("Executing: "+execute)
		logger.debug(execute)
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	def measure_storage(self):
		st = os.statvfs('/')
		self.spec['available_kb'] = (st.f_bavail * st.f_frsize) / 1024
		fs_size = st.f_blocks * st.f_frsize
		fs_used = (st.f_blocks - st.f_bfree) * st.f_frsize
		self.spec['used_storage'] = fs_used / float(fs_size)

	def measure_temperature(self):
		temp = cp.utils.get_temperature()
		if temp!=None:
			self.spec['temperature'] = float(temp/1000.0)

	#read the data from ping and reformat for database entry
	def parse_output(self, data, ethmac):
		self.spec["ethernet_MAC"]  = ethmac
		self.spec["current_MAC"]   = cp.utils.get_MAC()
		self.spec["source_address"]= cp.utils.get_SA()
		# shakey
		self.spec["local_address"] = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

		fields = data.split()
		#self.spec["uptime"] = fields[2][:-1]
		#self.spec["uptime"] = re.search("up .*?,",data).group(0)[3:-1]
		self.spec["uptime"] = float(uptime.uptime() / (60*60))
		self.spec["load1"]  = float(fields[-3][:-1])
		self.spec["load5"]  = float(fields[-2][:-1])
		self.spec["load15"] = float(fields[-1])

		return self.spec


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cp.config.get_dao()

	status_task = Status(dao)
	status_task.run()

