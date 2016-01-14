from __future__ import unicode_literals, absolute_import

from .result import Result
from .target import Target

class PingResult(Result):

	@classmethod
	def fromDict(cls, dct):
		assert dct['task_name'] == 'ping'

		p = PingResult()
		p._start_time = dct['start_time']
		p._end_time = dct['end_time']
		p._target = Target.fromDict(dct['target'])
		p._delay_sequence = dct['value']['delay_sequence']
		p._probe_count = dct['value']['probe_count']
		p._packet_loss = dct['value']['packet_loss']
		p._packet_size = dct['value']['packet_size']
		p._max_rtt = dct['value']['max_rtt']
		p._min_rtt = dct['value']['min_rtt']
		p._avg_rtt = dct['value']['avg_rtt']
		p._stddev_rtt = dct['value']['stddev_rtt']

		return p

	def toDict(self):
		return {
			'task_name':'ping',
			'start_time':self._start_time,
			'end_time':self._end_time,
			'target':self._target.toDict(),
			'value':{
				'delay_sequence':self._delay_sequence,
				'probe_count':self._probe_count,
				'packet_loss':self._packet_loss,
				'packet_size':self._packet_size,
				'max_rtt':self._max_rtt,
				'min_rtt':self._min_rtt,
				'avg_rtt':self._avg_rtt,
				'stddev_rtt':self._stddev_rtt,
			},
		}

	def taskname(self):
		return 'ping'
