from __future__ import unicode_literals, absolute_import

from .statistics import Statistics
from cheesepi.server.processing.utils import DistributionModel
from cheesepi.server.storage.models.entity import Entity

class PingStatistics(Statistics):

	@classmethod
	def fromDict(cls, dct):
		p = PingStatistics()
		p._target = Entity.fromDict(dct['target'])
		p._delay = DistributionModel.fromDict(dct['delay'])
		p._average_delay = DistributionModel.fromDict(dct['average_delay'])
		p._average_median_delay = DistributionModel.fromDict(dct['average_median_delay'])
		p._average_packet_loss = DistributionModel.fromDict(dct['average_packet_loss'])
		p._all_time_min_rtt = dct['all_time_min_rtt']
		p._all_time_max_rtt = dct['all_time_max_rtt']
		p._total_packet_loss = dct['total_packet_loss']
		p._total_probe_count = dct['total_probe_count']

		return p

	def __init__(self, target=None):
		self._target = target
		self._delay = DistributionModel()
		self._average_delay = DistributionModel()
		self._average_median_delay = DistributionModel()
		self._average_packet_loss = DistributionModel()
		self._all_time_min_rtt = 999999999
		self._all_time_max_rtt = 0
		self._total_packet_loss = 0
		self._total_probe_count = 0

	def toDict(self):
		return {
			'task_name':'ping',
			'target':self._target.toDict(),
			'delay':self._delay.toDict(),
			'average_delay':self._average_delay.toDict(),
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

	def get_delay(self):
		return self._delay
	def get_average_delay(self):
		return self._average_delay
	def get_average_median_delay(self):
		return self._average_median_delay
	def get_average_packet_loss(self):
		return self._average_packet_loss
	def get_all_time_min_rtt(self):
		return self._all_time_min_rtt
	def get_all_time_max_rtt(self):
		return self._all_time_max_rtt
	def get_total_packet_loss(self):
		return self._total_packet_loss
	def get_total_probe_count(self):
		return self._total_probe_count

	def absorb_result(self, result, upload_index=0):
		from cheesepi.server.processing.utils import median

		assert result.get_taskname() == 'ping'

		self._total_probe_count = self._total_probe_count + result.get_probe_count()
		self._total_packet_loss = self._total_packet_loss + result.get_packet_loss()
		self._all_time_min_rtt = min(self._all_time_min_rtt, result.get_min_rtt())
		self._all_time_max_rtt = max(self._all_time_max_rtt, result.get_max_rtt())

		# If we want to calculate the median we need a sequence without lost
		# packets
		pure_sequence = []
		for d in result.get_delay_sequence():
			# We need to ignore lost packets
			if d > 0:
				#self._delay.add_datum(d)
				pure_sequence.append(d)
		#self._delay.add_data2(pure_sequence)
		self._delay.add_data(pure_sequence, upload_index=upload_index)

		sequence_median = median(pure_sequence)
		#self.log.info("MEDIAN {}".format(sequence_median))
		self._average_median_delay.add_data(sequence_median, upload_index=upload_index)

		self._average_delay.add_data(result.get_avg_rtt(), upload_index=upload_index)
		#self.log.info("PACKET_LOSS {}".format(result.get_packet_loss()))
		#self.log.info("PROBE_COUNT {}".format(result.get_probe_count()))
		self._average_packet_loss.add_data(
		        float(result.get_packet_loss())/float(result.get_probe_count()),
		        upload_index=upload_index)
