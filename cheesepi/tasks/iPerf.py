import time
import os
import logging
from subprocess import Popen, PIPE

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

class iPerf(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "iperf"
		if not 'landmark' in spec: self.spec['landmark'] = "iperf.eenet.ee"
		if not 'port' in spec: self.spec['port'] = 5201


	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("iPerfing: %s:%d @ %f, PID: %d" % (self.spec['landmark'], self.spec['port'], time.time(), os.getpid()))
		self.measure()

	# measure and record funtion
	def measure(self):
		self.spec['start_time'] = cp.utils.now()
		op_output  = self.perform(self.spec['landmark'], self.spec['port'])
		self.spec['end_time']   = cp.utils.now()
		logger.debug(op_output)
		parsed_output = self.parse_output(op_output)
		self.dao.write_op(self.spec['taskname'], parsed_output)

	#ping function
	def perform(self, landmark, port):
		# an ARM version of this is located at 'client/tools/iperf3'
		execute = "iperf3 -yc -f k -p %d -c %s"%(port, landmark)
		print execute
		logging.info("Executing: "+execute)
		logger.debug(execute)
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	#read the data from ping and reformat for database entry
	def parse_output(self, data):

		lines = data.split("\n")
		fields = lines[0].split(',')
		self.spec['bandwidth'] = int(fields[-1])
		self.spec['transfer']  = int(fields[-2])
		return self.spec


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cp.config.get_dao()

	# Public servers https://iperf.fr/iperf-servers.php
	spec = {'landmark':"iperf.eenet.ee",
		'port':5201,
	}
	iperf_task = iPerf(dao, spec)
	iperf_task.run()

