from __future__ import unicode_literals, absolute_import

from .statistics import Statistics
from cheesepilib.server.processing.utils import StatObject
from cheesepilib.server.storage.models.target import Target

class PingStatistics(Statistics):

	@classmethod
	def fromDict(cls, dct):
		p = PingStatistics()
		p._target = Target.fromDict(dct['target'])
		p._mean_delay = StatObject.fromDict(dct['mean_delay'])
		p._average_median_delay = StatObject.fromDict(dct['average_median_delay'])
		p._average_packet_loss = StatObject.fromDict(dct['average_packet_loss'])
		p._all_time_min_rtt = dct['all_time_min_rtt']
		p._all_time_max_rtt = dct['all_time_max_rtt']
		p._total_packet_loss = dct['total_packet_loss']
		p._total_probe_count = dct['total_probe_count']

		return p

	def __init__(self, target=None):
		self._target = target
		self._mean_delay = StatObject(0,0)
		self._average_median_delay = StatObject(0,0)
		self._average_packet_loss = StatObject(0,0)
		self._all_time_min_rtt = 999999999
		self._all_time_max_rtt = 0
		self._total_packet_loss = 0
		self._total_probe_count = 0

	def toDict(self):
		return {
			'task_name':'ping',
			'target':self._target.toDict(),
			'mean_delay':self._mean_delay.toDict(),
			'average_median_delay':self._average_median_delay.toDict(),
			'average_packet_loss':self._average_packet_loss.toDict(),
			'all_time_min_rtt':self._all_time_min_rtt,
			'all_time_max_rtt':self._all_time_max_rtt,
			'total_packet_loss':self._total_packet_loss,
			'total_probe_count':self._total_probe_count,
		}

	def get_type(self):
		return 'ping'

	def get_target(self):
		return self._target

	def get_target_hash(self):
		return self._target.get_hash()

	def absorb_result(self, result):
		from cheesepilib.server.processing.utils import median

		assert result.get_taskname() == 'ping'

		self._total_probe_count = self._total_probe_count + result._probe_count
		self._total_packet_loss = self._total_packet_loss + result._packet_loss
		self._all_time_min_rtt = min(self._all_time_min_rtt, result._min_rtt)
		self._all_time_max_rtt = max(self._all_time_max_rtt, result._max_rtt)

		self._mean_delay.add_datum(result._avg_rtt)
		self._average_median_delay.add_datum(median(result._delay_sequence))
		self._average_packet_loss.add_datum(result._packet_loss/result._probe_count)
