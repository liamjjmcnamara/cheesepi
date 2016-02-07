from __future__ import unicode_literals, absolute_import

from .result import Result
from .entity import Entity

class PingResult(Result):

	@classmethod
	def fromDict(cls, dct):
		assert dct['task_name'] == 'ping'

		p = PingResult()
		p._start_time = dct['start_time']
		p._end_time = dct['end_time']
		p._target = Entity.fromDict(dct['target'])

		seq = dct['value']['delay_sequence']
		if isinstance(seq, str):
		    import ast
		    seq = ast.literal_eval(seq)
		p._delay_sequence = seq

		p._probe_count = dct['value']['probe_count']
		p._packet_loss = dct['value']['packet_loss']
		p._packet_size = dct['value']['packet_size']
		p._max_rtt = dct['value']['max_rtt']
		p._min_rtt = dct['value']['min_rtt']
		p._avg_rtt = dct['value']['avg_rtt']
		p._stddev_rtt = dct['value']['stddev_rtt']

		return p

	def __init__(self):
		self._start_time = 0
		self._end_time = 0
		self._target = None
		self._delay_sequence = None
		self._probe_count = 0
		self._packet_loss = 0
		self._packet_size = 0
		self._max_rtt = 0
		self._min_rtt = 0
		self._avg_rtt = 0
		self._stddev_rtt = 0

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

	def get_taskname(self):
		return 'ping'

	def get_target(self):
		return self._target

	def get_start_time(self):
		return self._start_time
	def get_end_time(self):
		return self._end_time
	def get_delay_sequence(self):
		return self._delay_sequence
	def get_probe_count(self):
		return self._probe_count
	def get_packet_loss(self):
		return self._packet_loss
	def get_packet_size(self):
		return self._packet_size
	def get_max_rtt(self):
		return self._max_rtt
	def get_min_rtt(self):
		return self._min_rtt
	def get_avg_rtt(self):
		return self._avg_rtt
	def get_stddev_rtt(self):
		return self._stddev_rtt
