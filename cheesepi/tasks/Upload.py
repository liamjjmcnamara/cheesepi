import sys
import time
import os

sys.path.append("/usr/local/")
import cheesepi
import Task

class Upload(Task.Task):
	"""Task to upload data to central server"""
	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "upload"
		if not 'server' in spec: self.spec['server'] = cheesepi.config.get_controller()

	def run(self):
		"""Upload data server, may take some time..."""
		print "Uploading data... @ %f, PID: %d" % (time.time(), os.getpid())


