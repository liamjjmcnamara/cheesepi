#!/usr/bin/env python2
from __future__ import unicode_literals, absolute_import, print_function

import pickle
import math

class Data(object):

	def pickle(self, path):
		with open(path, 'wb') as fd:
			pickle.dump(self, fd)

class DistData(Data):

	def __init__(self, source, target, original_distributions,
			distribution_model, samples):

		self._source = source
		self._target = target

		#self._x_values = x_values
		#self._y_original = y_original
		#self._y_model = y_model
		#self._x_hist = x_hist
		#self._y_hist = y_hist
		#self._n_samples = n_samples

		# Array of (iteration, distribution)
		self._original_distributions = original_distributions

		# DistributionModel object
		self._distribution_model = distribution_model

		# Samples
		self._samples = samples

class ValuesData(Data):

	def __init__(self, source, target, real_means, real_variances, real_skews,
			real_kurtosiss, uni_mean_values, uni_variance_values, exp_mean_values,
			exp_variance_values):

		self._source = source
		self._target = target

		# The actual values of the generating distributions
		self._real_means = real_means
		self._real_variances = real_variances
		# DEPRECATED
		self._real_skews = real_skews
		self._real_kurtosiss = real_kurtosiss

		# The values at given points in time, in arrays of tuples (index, value)
		self._uni_mean_values = uni_mean_values
		self._uni_variance_values = uni_variance_values
		self._exp_mean_values = exp_mean_values
		self._exp_variance_values = exp_variance_values

class DeltaData(Data):

	def __init__(self, source, target, delta_uni_mean, delta_uni_variance,
	        delta_exp_mean, delta_exp_variance):

		self._source = source
		self._target = target

		# Delta values in arrays of tuples (index, value)
		self._delta_uni_mean = delta_uni_mean
		self._delta_uni_variance = delta_uni_variance
		self._delta_exp_mean = delta_exp_mean
		self._delta_exp_variance = delta_exp_variance
