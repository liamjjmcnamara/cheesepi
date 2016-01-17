from __future__ import unicode_literals, absolute_import

import logging
from collections import namedtuple

from cheesepilib.server.storage.models.target import Target

TargetStatistic = namedtuple("TargetStatistic", ["target", "stat_type"])

class Statistics(object):
	log = logging.getLogger("cheesepi.server.storage.models.statistics.Statistics")

	@classmethod
	def fromDict(cls, dct):
		name = dct['task_name']

		from .PingStatistics import PingStatistics
		if name == 'ping': return PingStatistics.fromDict(dct)
		else: raise UnsupportedStatisticsType("Unknown statistics type '{}'.".format(name))

	@classmethod
	def fromName(cls, name, target):

		from .PingStatistics import PingStatistics
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
	"""
	A StatisticsSet can contain a set of statistics that can come from different
	tasks and for different targets.
	"""
	log = logging.getLogger("cheesepi.server.storage.models.statistics.StatisticsSet")

	@classmethod
	def fromDict(cls, dct):
		from pprint import pformat
		#target = Target.fromDict(dct['target'])
		stats_list = []
		#stats_set = {}
		#cls.log.info("\n{}".format(pformat(dct)))
		for target_hash in dct:
			for stat_type in dct[target_hash]:
				if stat_type == 'target':
					# TODO remnant, to remove later
					continue
				else:
					#target = Target.fromDict(dct[target_hash][stat_type]['target'])
					#stats_set[(target,stat_type)] = Statistics.fromDict(
							#dct[target_hash][stat_type])
					#cls.log.info(target_hash)
					#cls.log.info(stat_type)
					stats_list.append(Statistics.fromDict(dct[target_hash][stat_type]))
		#cls.log.info(stats_list)
		return cls.fromList(stats_list)

	@classmethod
	def fromList(cls, lst):

		ss = StatisticsSet()

		for statistic in lst:
			assert isinstance(statistic, Statistics)
			#cls.log.info(statistic)
			target_stat = TargetStatistic(target=statistic.get_target_hash(),
			                              stat_type=statistic.get_type())

			ss._statistics_set[target_stat] = statistic

		return ss

	def __init__(self): #target, statistics_set):
		"""
		Takes a target id and a list of statistics objects
		"""
		self._statistics_set = {}

	def __iter__(self):
		"""
		Returns an iterator over the Statistics objects in the dictionary
		"""
		return iter(self._statistics_set.values())

	def toDict(self):
		dct = {} #{'target':self._target}
		#self.log.info(self._statistics_set)
		for stat in self._statistics_set.itervalues():
			#self.log.info("#")
			#self.log.info(stat)
			#self.log.info("#")
			stat_dct = stat.toDict()
			dct[stat_dct['task_name']] = stat_dct
		return dct

	def absorb_results(self, result_list):
		"""
		Takes a list of results and updates all statistics objects accordingly
		"""

		for result in result_list:

			task_name = result.get_taskname()
			target = result.get_target()
			target_hash = target.get_hash()

			target_stat = TargetStatistic(target=target_hash, stat_type=task_name)

			if target_stat not in self._statistics_set:
				self.log.info("TargetStat '{}' not present in set, inserting.".format(target_stat))
				self._statistics_set[target_stat] = Statistics.fromName(task_name,
				                                                        target)
			self._statistics_set[target_stat].absorb_result(result)
