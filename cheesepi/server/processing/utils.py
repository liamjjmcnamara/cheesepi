from __future__ import unicode_literals, absolute_import, print_function

import logging
import math
import tarfile
import hashlib

# Processing functions, untar, calculating stats etc...
# TODO some kind of logging??
# How do we know where the database is???

def process_upload(uploaded_file):
	from .ResultDataProcessor import ResultDataProcessor

	with ResultDataProcessor(uploaded_file) as data:
		data.process()

# TODO Maybe this should be baked into ResultDataProcessor
def untar(filename, destination):
	with tarfile.open(filename) as tar:
		tar.extractall(destination)

def md5_filehash(filepath):
	hasher = hashlib.md5()
	with open(filepath) as fd:
		hasher.update(fd.read())
	return hasher.hexdigest()

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
	log = logging.getLogger("cheesepi.server.processing.StatObject")

	_DEFAULT_ALPHA = 0.5

	@classmethod
	def fromDict(cls, dct):
		"""
		Parses a dict object which should contain the keys 'value'
		"""
		try:
			mean = dct['mean']
			variance = dct['variance']
			return cls(mean, variance)
		except (KeyError,TypeError) as e:
			cls.log.exception("{} while parsing dict.".format(e.__class__.__name__))
			return cls(0, 0)

	def toDict(self):
		return {
			'mean':self._mean,
			'variance':self._variance,
			'std_dev':self._std_dev,
		}

	def __init__(self, mean=0, variance=0, alpha=_DEFAULT_ALPHA):
		self._mean = mean
		self._variance = variance
		self._std_dev = math.sqrt(variance)
		self._alpha = self._DEFAULT_ALPHA

	def __repr__(self):
		return "StatObject({mean}, {variance}, {std_dev}, alpha={alpha})".format(
				mean=self._mean,
				variance=self._variance,
				std_dev=self._std_dev,
				alpha=self._alpha)

	def set_alpha(self, alpha):
		self._alpha = alpha

	def get_mean(self):
	    return self._mean
	def get_variance(self):
	    return self._variance
	def get_std_dev(self):
	    return self._std_dev
	def get_alpha(self):
	    return self._alpha

	def add_datum(self, new_datum, alpha=_DEFAULT_ALPHA):
		"""
		Add a new data point
		"""
		delta = new_datum - self._mean
		increment = alpha * delta

		self._mean = self._mean + increment
		self._variance = (1-alpha) * (self._variance + (delta * increment))
		self._std_dev = math.sqrt(self._variance)
