import sys

sys.path.append("/usr/local/")
import Task

class Reschedule(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "reschedule"

	def run(self):
		print "Warning: Reschedule tasks should not be run!"


