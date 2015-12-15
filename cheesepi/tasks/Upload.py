import sys
import time
import os

sys.path.append("/usr/local/")
import Task

class Upload(Task.Task):
	"""Task to upload data to central server"""
	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "upload"
		self.server      = "cheesepi.sics.se"
		if 'server' in parameters: self.server = parameters['server']

	def toDict(self):
		return {'taskname'   :self.taskname,
				}

	def run(self):
		"""Upload data server, may take some time..."""
		print "Uploading data... @ %f, PID: %d" % (time.time(), os.getpid())


