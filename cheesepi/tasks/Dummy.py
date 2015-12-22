import sys
import time
import os

sys.path.append("/usr/local/")
import cheesepi.utils
import Task

class Dummy(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "dummy"
		if not 'message' in self.spec: self.spec['message'] = "This is not a test"

	# actually perform the measurements, no arguments required
	def run(self):
		print "Dummy: %s @ %f, PID: %d" % (self.spec['message'], time.time(), os.getpid())


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	#parameters = {'landmark':'google.com','ping_count':10,'packet_size':64}
	spec = {}
	dummy_task = Dummy(dao, spec)
	dummy_task.run()

