from __future__ import unicode_literals, absolute_import

from cheesepilib.server.storage.models.target import Target

class Statistics(object):

	@classmethod
	def fromDict(cls, target, dct):
		name = dct['task_name']

		from .PingStatistics import PingStatistics
		if name == 'ping': return PingStatistics.fromDict(target, dct)
		else: raise UnsupportedStatisticsType("Unknown statistics type '{}'.".format(name))

	@classmethod
	def fromName(cls, name, target):

		if name == 'ping': return PingStatistics(target)
		else: raise UnsupportedStatisticsType("Unknown statistics type '{}'.".format(name))
	def get_type(self):
		raise NotImplementedError("Abstract method 'get_type' not implemented.")

	def get_target(self):
		raise NotImplementedError("Abstract method 'get_target' not implemented.")

	def get_target_hash(self):
		raise NotImplementedError("Abstract method 'get_target_hash' not implemented.")

	def toDict(self):
		raise NotImplementedError("Abstract method 'toDict' not implemented.")

class StatisticsSet(object):

	@classmethod
	def fromDict(cls, dct):
		target = Target.fromDict(dct['target'])
		stats_set = {}
		for key in dct:
			if key == 'target':
				continue
			else:
				assert key not in stats_set
				stats_set[key] = Statistics.fromDict(target, dct[key])
		return StatisticsSet(target, stats_set)

	def __init__(self, target, statistics_set):
		"""
		Takes a target id and a list of statistics objects
		"""
		self._target = target
		self._statistics_set = statistics_set

	def __iter__(self):
		"""
		Returns an iterator over the Statistics objects in the dictionary
		"""
		return iter(self._statistics_set.values())

	def toDict(self):
		dct = {'target':self._target}
		for stat in self._statistics_set.itervalues():
			stat_dct = stat.toDict()
			dct[stat_dct['task_name']] = stat_dct
		return dct

	def absorb_results(self, result_list):
		"""
		Takes a list of results and updates all statistics objects accordingly
		"""

		for result in result_list:

			task_name = result.taskname()
			if task_name not in self._statistics_set:
				self._statistics_set[task_name] = Statistics.fromName(task_name)

			self._statistics_set[task_name].absorb_result(result)
