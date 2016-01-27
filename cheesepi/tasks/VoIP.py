import time
import os
from subprocess import Popen, PIPE

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

class VoIP(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "voip"
		if not 'peer'    in self.spec: self.spec['peer']    = "somehost.com"

	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("Ringing: %s @ %f, PID: %d" % (self.spec['landmark'], time.time(), os.getpid()))
		self.measure()

	# measure and record funtion
	def measure(self):
		start_time = cp.utils.now()
		#op_output = self.perform(self.spec['landmark'], self.spec['ping_count'], self.spec['packet_size'])
		end_time = cp.utils.now()
		#logger.debug(op_output)
		#parsed_output = self.parse_output(op_output, self.spec['landmark'])
		#self.dao.write_op(self.spec['taskname'], parsed_output)

	#ping function
	def perform(self, landmark, ping_count, packet_size):
		pass

	#read the data from ping and reformat for database entry
	def parse_output(self, data, peer):
		pass


if __name__ == "__main__":
	dao = cp.config.get_dao()

	spec = {}
	voip_task = VoIP(dao, spec)
	voip_task.run()
	print voip_task.spec

