from __future__ import unicode_literals, absolute_import

import logging
from collections import namedtuple

from cheesepi.server.storage.models.entity import Entity

TargetStatistic = namedtuple("TargetStatistic", ["target", "stat_type"])

class Statistics(object):
	log = logging.getLogger("cheesepi.server.storage.models.statistics.Statistics")

	@classmethod
	def fromDict(cls, dct):
		name = dct['task_name']

		from cheesepi.server.storage.models.PingStatistics import PingStatistics
		if name == 'ping': return PingStatistics.fromDict(dct)
		else: raise UnsupportedStatisticsType("Unknown statistics type '{}'.".format(name))

	@classmethod
	def fromName(cls, name, target):

		from cheesepi.server.storage.models.PingStatistics import PingStatistics
		if name == 'ping': return PingStatistics(target)
		else: raise UnsupportedStatisticsType("Unknown statistics type '{}'.".format(name))
	def get_type(self):
		raise NotImplementedError("Abstract method 'get_type' not implemented.")

	def get_target(self):
		raise NotImplementedError("Abstract method 'get_target' not implemented.")

	def toDict(self):
		raise NotImplementedError("Abstract method 'toDict' not implemented.")

class StatisticsSet(object):
	"""
	A StatisticsSet can contain a set of statistics that can come from different
	tasks and for different targets.
	"""
	log = logging.getLogger("cheesepi.server.storage.models.statistics.StatisticsSet")

	@classmethod
	def fromDict(cls, dct):
		from pprint import pformat
		stats_list = []
		for target_uuid in dct:
			for stat_type in dct[target_uuid]:
				stats_list.append(Statistics.fromDict(dct[target_uuid][stat_type]))
		return cls.fromList(stats_list)

	@classmethod
	def fromList(cls, lst):
		ss = StatisticsSet()

		for statistic in lst:
			assert isinstance(statistic, Statistics)
			target_stat = TargetStatistic(target=statistic.get_target().get_uuid(),
			                              stat_type=statistic.get_type())

			ss._statistics_set[target_stat] = statistic

		return ss

	def __init__(self):
		"""
		Takes a target id and a list of statistics objects
		"""
		self._statistics_set = {}

	def __iter__(self):
		"""
		Returns an iterator over the Statistics objects in the dictionary
		"""
		return iter(self._statistics_set.values())

	def get_stats_for_target(self, target_uuid):

		keys = filter(lambda x: x[0] == target_uuid, self._statistics_set.keys())

		return [self._statistics_set[key] for key in keys]

	def toDict(self):
		dct = {}
		for target_stat, stat in self._statistics_set.iteritems():

			key = target_stat.target
			value = stat.toDict()

			if key not in dct:
				dct[key] = {}

			dct[key][value['task_name']] = value

		return dct

	def absorb_results(self, result_list, upload_index=0):
		"""
		Takes a list of results and updates all statistics objects accordingly
		"""

		for result in result_list:

			task_name = result.get_taskname()
			target = result.get_target()
			target_uuid = target.get_uuid()

			target_stat = TargetStatistic(target=target_uuid, stat_type=task_name)

			if target_stat not in self._statistics_set:
				self.log.info("TargetStat '{}' not present in set, inserting.".format(target_stat))
				stat = Statistics.fromName(task_name, target)
				self._statistics_set[target_stat] = stat
			self._statistics_set[target_stat].absorb_result(result, upload_index=upload_index)
