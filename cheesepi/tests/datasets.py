#!/usr/bin/env python2
from __future__ import unicode_literals, absolute_import, print_function

import pickle

class Data(object):

	def pickle(self, path):
		with open(path, 'wb') as fd:
			pickle.dump(self, fd)

class DistData(Data):

	def __init__(self, source, target, x_values, y_original, y_model,
			x_hist, y_hist, n_samples, distribution_model):

		self._source = source
		self._target = target

		self._x_values = x_values
		self._y_original = y_original
		self._y_model = y_model
		self._x_hist = x_hist
		self._y_hist = y_hist
		self._n_samples = n_samples

		self._dist_model = distribution_model

class ValuesData(Data):

	def __init__(self, source, target, real_mean, real_variance, real_skew,
			real_kurtosis, mean_values, variance_values, skew_values,
			kurtosis_values):

		self._source = source
		self._target = target

		# The actual values of the generating distribution
		self._real_mean = real_mean
		self._real_variance = real_variance
		self._real_skew = real_skew
		self._real_kurtosis = real_kurtosis

		# The values at given points in time, in arrays of tuples (index, value)
		self._mean_values = mean_values
		self._variance_values = variance_values
		self._skew_values = skew_values
		self._kurtosis_values = kurtosis_values

class DeltaData(Data):

	def __init__(self, source, target, delta_mean, delta_variance, delta_skew,
			delta_kurtosis):

		self._source = source
		self._target = target

		# Delta values in arrays of tuples (index, value)
		self._delta_mean = delta_mean
		self._delta_variance = delta_variance
		self._delta_skew = delta_skew
		self._delta_kurtosis = delta_kurtosis
