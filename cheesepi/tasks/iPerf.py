import sys
import time
import os
import logging
from subprocess import Popen, PIPE

sys.path.append("/usr/local/")
import cheesepi.utils
import Task

class iPerf(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "iperf"
		if not 'landmark' in spec: self.spec['landmark'] = "iperf.eenet.ee"
		if not 'port' in spec: self.spec['port'] = 5201


	# actually perform the measurements, no arguments required
	def run(self):
		print "iPerfing: %s:%d @ %f, PID: %d" % (self.spec['landmark'], self.spec['port'], time.time(), os.getpid())
		self.measure()

	# measure and record funtion
	def measure(self):
		self.spec['start_time'] = cheesepi.utils.now()
		op_output  = self.perform(self.landmark, self.port)
		self.spec['end_time']   = cheesepi.utils.now()
		#print op_output
		parsed_output = self.parse_output(op_output)
		self.dao.write_op(self.spec['taskname'], parsed_output)

	#ping function
	def perform(self, landmark, port):
		execute = "iperf -yc -p %d -c %s"%(port, landmark)
		logging.info("Executing: "+execute)
		#print execute
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	#read the data from ping and reformat for database entry
	def parse_output(self, data, landmark, start_time, end_time):

		lines = data.split("\n")
		fields = lines[0].split(',')
		self.spec['bandwidth'] = fields[-1]
		self.spec['transfer']  = fields[-2]
		return self.spec


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	# Public servers https://iperf.fr/iperf-servers.php
	spec = {'landmark':"iperf.eenet.ee",
		'port':5201,
	}
	iperf_task = iPerf(dao, spec)
	iperf_task.run()
