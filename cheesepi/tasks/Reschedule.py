import sys

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

	def run(self):
		print "Warning: Reschedule tasks should not be run!"


