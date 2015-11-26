import json


# To be subclassed by explicit measurement tasks
class Task:

	def __init__(self, dao, parameters):
		self.taskname = "Superclass"
		self.dao      = dao
		self.cycle    = 0
		if 'cycle' in parameters:
			self.cycle    = parameters['cycle']

	def toDict(self):
		return {'taskname':'superclass'}

	def toJson(self):
		return json.dumps(self.toDict())

	# this will be overridden by subclasses
	def run(self):
		print "Task not doing anything..."


