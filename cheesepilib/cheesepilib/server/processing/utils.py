from __future__ import unicode_literals, absolute_import, print_function

import math
import tarfile

# Processing functions, untar, calculating stats etc...
# TODO some kind of logging??
# How do we know where the database is???

def process_upload(uploaded_file):
	from .ResultDataProcessor import ResultDataProcessor

	with ResultDataProcessor(uploaded_file) as data:
		data.process()
		print("Done processing.")

# TODO Maybe this should be baked into ResultDataProcessor
def untar(filename, destination):
	with tarfile.open(filename) as tar:
		tar.extractall(destination)

# This might be better to include from a well maintained library
def median(input_list):
	lst = sorted(input_list)
	if len(lst) < 1:
		return 0
	if len(lst) % 2 == 1:
		return lst[((len(lst)+1)/2)-1]
	else:
		return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0

class StatObject(object):
	"""
	TODO maybe rename to something better

	Keeps track of mean value, variance and standard deviation incrementally
	while new data is supplied.
	"""

	_DEFAULT_ALPHA = 0.5

	def __init__(self, mean=0, variance=0, alpha=_DEFAULT_ALPHA):
		self.mean = mean
		self.variance = variance
		self.std_dev = math.sqrt(variance)
		self.alpha = self._DEFAULT_ALPHA

	def __repr__(self):
		return "StatObject({mean}, {variance}, {std_dev}, alpha={alpha})".format(
				mean=self.mean,
				variance=self.variance,
				std_dev=self.std_dev,
				alpha=self.alpha)

	def set_alpha(self, alpha):
		self.alpha = alpha

	def add_datum(self, new_datum, alpha=_DEFAULT_ALPHA):
		"""
		Add a new data point
		"""
		delta = new_datum - self.mean
		increment = alpha * delta

		self.mean = self.mean + increment
		self.variance = (1-alpha) * (self.variance + (delta * increment))
		self.std_dev = math.sqrt(self.variance)
