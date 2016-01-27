import time
import os

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

class Dummy(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "dummy"
		if not 'message' in self.spec: self.spec['message'] = "This is not a test"

	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("Dummy: %s @ %f, PID: %d" % (self.spec['message'], time.time(), os.getpid()))


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cp.config.get_dao()

	spec = {}
	dummy_task = Dummy(dao, spec)
	dummy_task.run()

