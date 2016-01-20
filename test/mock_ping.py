from __future__ import unicode_literals, absolute_import, print_function

import random
import math
import sys
import json

import numpy as np

from scipy.stats import gamma

class PingResultMocker(object):

	def __init__(self, shape=2, loc=10, scale=3, lossrate=0, seed=None):

		if seed is not None:
			np.random.seed(seed)

		if shape is None:
			shape = 2
		if loc is None:
			loc = 10
		if scale is None:
			scale = 3

		self._shape = shape
		self._loc = loc
		self._scale = scale
		self._generate_dist()

	def _generate_dist(self):
		self._dist = gamma(self._shape, loc=self._loc, scale=self._scale)

	def sample_n(self, n):
		samples = self._dist.rvs(size=n)
		if lossrate != 0:
			for i in range(0, len(samples)):
				if random.uniform(0,1) < lossrate:
					samples[i] = -1

		return samples


	def set_seed(self, seed):
		np.random.seed(seed)
	def set_shape(self, shape):
		self._shape = shape
		self._generate_dist()
	def set_loc(self, loc):
		self._loc = loc
		self._generate_dist()
	def set_scale(self, scale):
		self._scale = scale
		self._generate_dist()

	def get_mean(self):
		return self._dist.stats(moments='m').item()
	def get_variance(self):
		return self._dist.stats(moments='v').item()
	def get_std_dev(self):
		return math.sqrt(self._dist.stats(moments='v').item())
	def get_skew(self):
		return self._dist.stats(moments='s').item()
	def get_kurtosis(self):
		return self._dist.stats(moments='k').item()

class PingResultObjectConstructor(object):

	def __init__(self, peer_id):
		self._peer_id = peer_id
		self._results = []

	def add_result(self, data, target_id, destination_address):
		# TODO packet loss assumed 0 for now but should extend so we can model
		# that as well in the future
		max_rtt = 0
		min_rtt = sys.maxint
		stddev_rtt = 0
		average_rtt = 0
		packet_loss = 0
		ping_count = len(data)

		total_sum = 0
		square_sum = 0
		for d in data:
			# Make sure to catch packet loss before anything else
			if d < 0:
				packet_loss = packet_loss + 1
				continue

			if d < min_rtt:
				min_rtt = d
			if d > max_rtt:
				max_rtt = d
			total_sum = total_sum + d
			square_sum = square_sum + math.pow(d, 2)

		# NOTE We need to account for lost packets when calculating things
		success_count = ping_count - packet_loss

		variance = square_sum/success_count

		stddev_rtt = math.sqrt(variance)
		average_rtt = total_sum/success_count


		result = [
		    self._peer_id,
		    target_id,
		    None,
		    None,
		    str(data),
		    destination_address,
		    None,
		    None,
		    None,
		    None,
		    max_rtt,
		    min_rtt,
		    None,
		    packet_loss,
		    None,
		    None,
		    ping_count,
		    None,
		    None,
		    None,
		    stddev_rtt,
		    'ping',
		    average_rtt,
		    None,
		    None,
		]

		self._results.append(result)

	def construct(self):
		columns = [
		    "peer_id",
		    "target_id",
		    "time",
		    "cycle",
		    "delays",
		    "destination_address",
		    "destination_domain",
		    "downloaded",
		    "end_time",
		    "landmark",
		    "maximum_RTT",
		    "minimum_RTT",
		    "offset",
		    "packet_loss",
		    "packet_size",
		    "period",
		    "ping_count",
		    "sign",
		    "source",
		    "start_time",
		    "stddev_RTT",
		    "taskname",
		    "average_RTT",
		    "uploaded",
		    "version"
		]
		values = []
		for result in self._results:
			values.append(result)
		obj = [{'series':[{'values':values,'name':'ping','columns':columns}]}]
		return obj

if __name__ == "__main__":
	import argparse
	import ast
	from pprint import pformat

	parser = argparse.ArgumentParser()
	parser.add_argument('--peerid', type=str, default='1',
	                    help='the peer id the results belong to')
	parser.add_argument('--samplesize', type=int, default=10,
	                    help='number of samples for each result')
	parser.add_argument('--target', type=str, action='append',
	        help='the targets on the form: "{\'id\':id,\'ip\':ip}" with optional arguments \'shape\', \'loc\', \'scale\' and \'lossrate\' to modify the distribution')
	parser.add_argument('--seed', type=int, default=None,
	                    help='a random number seed')

	args = parser.parse_args()

	seed = args.seed
	proc = PingResultObjectConstructor(args.peerid)
	dist_stats = {}

	for t in args.target:
		dct = ast.literal_eval(t)
		shape = None
		loc = None
		scale = None
		lossrate = None
		if 'shape' in dct:
			shape = dct['shape']
		if 'loc' in dct:
			loc = dct['loc']
		if 'scale' in dct:
			scale = dct['scale']
		if 'lossrate' in dct:
			lossrate = dct['lossrate']

		prm = PingResultMocker(shape=shape, loc=loc, scale=scale,
		                       lossrate=lossrate, seed=seed)
		samples = prm.sample_n(args.samplesize)

		proc.add_result(list(samples), dct['id'], dct['ip'])

		dist = {
			'mean':prm.get_mean(),
			'variance':prm.get_variance(),
			'std_dev':math.sqrt(prm.get_variance()),
			'skew':prm.get_skew(),
			'kurt':prm.get_kurtosis(),
		}

		dist_stats[dct['id']] = dist

		# Make sure we get different sets from every target even if the
		# distribution is identical
		if seed is not None:
			seed = seed + 1

	obj = proc.construct()
	obj[0]['series'][0]['distribution_stats'] = dist_stats

	print(json.dumps(obj, indent=4, sort_keys=True))

	#import matplotlib.pyplot as plt
	#plt.hist(samples, 100)
	#plt.show()
