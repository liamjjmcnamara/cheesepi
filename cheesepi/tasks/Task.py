import json


# To be subclassed by explicit measurement tasks
class Task:

	def __init__(self, dao, parameters):
		self.taskname = "Superclass"
		self._result   = {} # how did it all go?
		self.dao      = dao
		self.cycle    = 0 # deprecated
		self.period   = 3600 # hourly
		self.offset   = 0
		if 'cycle' in parameters: self.cycle = parameters['cycle']

	def toDict(self):
		return {'taskname':'superclass'}

	def toJson(self):
		return json.dumps(self.toDict())

	# this will be overridden by subclasses
	def run(self):
		print "Task not doing anything..."

	def result(self):
		self._result['taskname'] = self.taskname
		self._result['downloaded'] = 1 # bytes, placeholder
		self._result['uploaded'] = 1 # bytes, placeholder
		return self._result
