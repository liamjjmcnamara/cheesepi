import sys
import time
import os
import logging

sys.path.append("/usr/local/")
import Task

class Reschedule(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "reschedule"
		self.cycle       = parameters['cycle']

	def toDict(self):
		return {'taskname'   :self.taskname,
				'cycle'      :self.cycle,
				}

	# actually perform the measurements, no arguments required
	def run(self):
		print "Pinging: %s @ %f, PID: %d" % (self.landmark, time.time(), os.getpid())
		self.measure(self.landmark, self.ping_count, self.packet_size)


