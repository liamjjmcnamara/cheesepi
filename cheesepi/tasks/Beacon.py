import sys
import time
import os

sys.path.append("/usr/local/")
import Task

class Beacon(Task.Task):
	"""Inform the central server that we are alive"""

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "beacon"
		self.server      = "cheesepi.sics.se"
		if 'server' in parameters: self.server = parameters['server']

	def toDict(self):
		return {'taskname'   :self.taskname,
				'cycle'      :self.cycle,
				}

	def run(self):
		print "Beaconing to %s @ %f, PID: %d" % (self.server, time.time(), os.getpid())
		self.beacon()

	def beacon(self):
		pass
