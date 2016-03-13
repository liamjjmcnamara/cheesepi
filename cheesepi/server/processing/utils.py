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

	return True

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

class DistributionModel(object):
	"""
	TODO implement incremental calculation of skewness and kurtosis

	Keeps track of mean value, variance and standard deviation incrementally
	while new data is supplied.
	"""
	log = logging.getLogger("cheesepi.server.processing.DistributionModel")

	_DEFAULT_ALPHA = 0.001

	@classmethod
	def fromDict(cls, dct):
		"""
		Parses a dict object which should contain the keys 'value'
		"""
		try:
			uni_mean = dct['uni_mean']
			uni_variance = dct['uni_variance']
			exp_mean = dct['exp_mean']
			exp_variance = dct['exp_variance']

			n = dct['n']
			# m1 = dct['m1']
			m2 = dct['m2']
			alpha = dct['alpha']
			# m3 = dct['m3']
			# m4 = dct['m4']
			# new_variance = dct['new_variance']
			# skew = dct['skew']
			# kurtosis = dct['kurtosis']
			# return cls(mean, variance, n, m1, m2, m3, m4, new_variance, skew, kurtosis)
			return cls(n, uni_mean, uni_variance, m2, exp_mean, exp_variance, alpha)
		except (KeyError,TypeError) as e:
			cls.log.exception("{} while parsing dict.".format(e.__class__.__name__))
			return cls()

	def toDict(self):
		return {
			'uni_mean':self._uni_mean,
			'uni_variance':self._uni_variance,
			'exp_mean':self._exp_mean,
			'exp_variance':self._exp_variance,
			# 'std_dev':self._std_dev,
			'n':self._n,
			# 'm1':self._m1,
			'm2':self._m2,
			'alpha':self._alpha,
			# 'm3':self._m3,
			# 'm4':self._m4,
			# 'new_variance':self._new_variance,
			# 'skew':self._skew,
			# 'kurtosis':self._kurtosis,
		}

	# def __init__(self, mean=0, variance=0, n=0, m1=0, m2=0, m3=0, m4=0,
	# 		new_variance=0, skew=0, kurtosis=0, alpha=_DEFAULT_ALPHA):
	def __init__(self, n=0, uni_mean=0, uni_variance=0, m2=0,
			exp_mean=0, exp_variance=0, alpha=_DEFAULT_ALPHA):

		self._alpha = alpha

		self._n = n

		self._uni_mean = uni_mean
		self._uni_variance = uni_variance
		self._m2 = m2 #TODO Needed?

		self._exp_mean = exp_mean
		self._exp_variance = exp_variance

		#self._m1 = m1
		#self._m3 = m3
		#self._m4 = m4

		#self._new_variance = new_variance
		#self._skew = skew
		#self._kurtosis = kurtosis

	def __repr__(self):
		return "DistributionModel({mean}, {variance}, alpha={alpha})".format(
				mean=self._uni_mean,
				variance=self._uni_variance,
				alpha=self._alpha)

	def set_alpha(self, alpha):
		self._alpha = alpha

	def get_mean(self):
		return self.get_uni_mean()
	def get_variance(self):
		return self.get_uni_variance()
	def get_std_dev(self):
		return self.get_uni_std_dev()

	# Exponentially weighted
	def get_exp_mean(self):
		return self._exp_mean
	def get_exp_variance(self):
		return self._exp_variance
	def get_exp_std_dev(self):
		return math.sqrt(self._exp_variance)

	# Uniformly weighted
	def get_uni_mean(self):
		return self._uni_mean
	def get_uni_variance(self):
		return self._uni_variance
	def get_uni_std_dev(self):
		return math.sqrt(self._uni_variance)

	def get_alpha(self):
		return self._alpha

	# def add_datum(self, new_datum, alpha=_DEFAULT_ALPHA):
	# 	"""
	# 	Add a new data point
	# 	"""
	# 	delta = new_datum - self._mean
	# 	increment = alpha * delta

	# 	self._mean = self._mean + increment
	# 	self._variance = (1-alpha) * (self._variance + (delta * increment))
	# 	self._std_dev = math.sqrt(self._variance)

	# def add_data2(self, samples, alpha=_DEFAULT_ALPHA):
	# 	"""
	# 	Doesn't work....
	# 	"""

	# 	n = len(samples)
	# 	sample_sum = 0
	# 	for x in samples:
	# 		sample_sum = sample_sum + x

	# 	sample_mean = sample_sum/n

	# 	delta = sample_mean - self._mean
	# 	increment = alpha * delta

	# 	self._mean = self._mean + increment
	# 	self._variance = (1-alpha) * (self._variance + (delta * increment))
	# 	self._std_dev = math.sqrt(self._variance)

	def add_data(self, samples, upload_index):
		# TODO remove upload_index??
		self.add_data_uniform(samples, upload_index)
		self.add_data_exponential(samples, upload_index)

	def add_data_uniform(self, samples, upload_index):

		if not isinstance(samples, list):
			samples = [samples]

		n = self._n
		mean = float(self._uni_mean)
		m2 = float(self._m2)

		for x in samples:
			n = n + 1
			delta = x - mean
			mean = mean + delta / n
			m2 = m2 + delta * (x - mean)

		self._n = n
		self._m2 = m2
		self._uni_mean = mean
		self._uni_variance = m2 / max((n - 1), 1)

	def add_data_exponential(self, samples, upload_index):

		if not isinstance(samples, list):
			samples = [samples]

		alpha = self._alpha
		mean = self._exp_mean
		variance = self._exp_variance

		for x in samples:
			delta = x - mean
			increment = alpha * delta

			mean = mean + increment
			variance = (1-alpha) * (variance + (delta * increment))

		self._exp_mean = mean
		self._exp_variance = variance


	# def old_add_data(self, samples, upload_index=0):
	# 	"""
	# 	Update the distribution model with the new samples
	# 	"""
	# 	n = self._n      # Number of samples
	# 	m1 = self._m1    # Mean
	# 	m2 = self._m2
	# 	m3 = self._m3
	# 	m4 = self._m4

	# 	for x in samples:
	# 		old_n = n
	# 		n = n + 1

	# 		delta_m1 = x - m1
	# 		norm_delta_m1 = delta_m1/n
	# 		norm_delta_m1_sq = norm_delta_m1 * norm_delta_m1

	# 		delta_m2 = delta_m1 * norm_delta_m1 * old_n
	# 		#norm_delta_m2 = delta_m2 / n

	# 		m4 = m4 + (
	# 			delta_m2 * norm_delta_m1_sq * (n*n - 3*n + 3)
	# 			+
	# 			6 * norm_delta_m1_sq * m2
	# 			-
	# 			4 * norm_delta_m1 * m3
	# 		)

	# 		m3 = m3 + (
	# 			delta_m2 * norm_delta_m1 * (n-2)
	# 			-
	# 			3 * norm_delta_m1 * m2
	# 		)

	# 		m2 = m2 + delta_m2

	# 		# Mean (the first moment is already normalized)
	# 		m1 = m1 + norm_delta_m1

	# 	if n < 1:
	# 		return # No information gained anyway....
	# 	elif n == 1:
	# 		# We need to avoid division by zero here
	# 		div = 1
	# 		# If we only got one sample, chances are that m2 is 0.0
	# 		if m2 == 0.0:
	# 			m2 = 1.0
	# 	else:
	# 		div = n-1

	# 	# Normalized Variance (n-1 because for n=1 the second moment is 0)
	# 	new_variance = (m2 / div)

	# 	# Standard deviation
	# 	std_dev = math.sqrt(new_variance)

	# 	# Skewness
	# 	skew = (m3/div) / math.pow(std_dev, 3)

	# 	# Kurtosis, adjusted so kurtosis of Gauss = 0
	# 	kurtosis = (m4/div) / math.pow(std_dev, 4) - 3

	# 	self.log.info("Result index is {}".format(upload_index))
	# 	self.log.info("dm1 = {}".format(math.fabs(self._m1 - m1)))

	# 	self._new_variance = new_variance
	# 	self._skew = skew
	# 	self._kurtosis = kurtosis

	# 	self._n = n
	# 	self._m1 = m1
	# 	self._m2 = m2
	# 	self._m3 = m3
	# 	self._m4 = m4
