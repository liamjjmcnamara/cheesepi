from __future__ import unicode_literals, absolute_import, print_function

import random
import math
import sys


class PingMocker(object):

	def __init__(self, num, min_val, max_val):

		self._num = num
		self._min_val = min_val
		self._max_val = max_val

		self._mean = 0
		self._minimum = 0
		self._maximum = 0
		self._variance = 0
		self._std_dev = 0

		self.regenerate()

	def __repr__(self):
		from pprint import pformat
		data = pformat(self._data)
		stats = "min: {} max: {} mean: {} variance: {} std_dev: {}".format(
			self._minimum, self._maximum, self._mean, self._variance,
			self._std_dev)
		return "Data:\n{}\nStats:\n{}".format(data, stats)

	def regenerate(self):
		self._data = []

		minimum = sys.maxint
		maximum = 0
		total_sum = 0

		for n in range(0, self._num):
			self._data.append(random.uniform(self._min_val, self._max_val))

			total_sum = total_sum + self._data[n]

			if self._data[n] < minimum:
				minimum = self._data[n]
			elif self._data[n] > maximum:
				maximum = self._data[n]

		self._minimum = minimum
		self._maximum = maximum
		self._mean = total_sum/self._num

		square_sum = 0
		for n in range(0, self._num):
			delta_square = math.pow(self._data[n] - self._mean, 2)
			square_sum = square_sum + delta_square

		self._variance = square_sum/self._num
		self._std_dev = math.sqrt(self._variance)

	def _caculate_variance_and_std_dev(self):
		pass


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('--num', type=int, default=10,
	                    help='number of data points')
	parser.add_argument('--min', type=int, default=8,
	                    help='the minimum value for any data point')
	parser.add_argument('--max', type=int, default=12,
	                    help='the maximum value for any data point')

	args = parser.parse_args()

	pm = PingMocker(args.num, args.min, args.max)

	print(pm)
