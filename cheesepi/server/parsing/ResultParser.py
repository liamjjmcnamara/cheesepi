from __future__ import unicode_literals, absolute_import, print_function

import json

from cheesepi.exceptions import UnsupportedResultType

class ResultParser(object):

	def __enter__(self):
		self.parse()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass

	@classmethod
	def fromFile(cls, filename):
		with open(filename) as fd:
			json_obj = json.load(fd)
		return cls.fromJson(json_obj)

	@classmethod
	def fromJson(cls, json_obj):
		from .PingResultParser import PingResultParser

		name = cls.get_taskname(json_obj)

		if name == 'ping': return PingResultParser(json_obj)
		else: raise UnsupportedResultType("Unknown task type '{}'.".format(name))

	@staticmethod
	def get_taskname(obj):
		return obj[0]['series'][0]['name']

	def parse(self):
		raise NotImplementedError(
		        "Abstract method 'parse' not implemented")

	def get_result_set():
		raise NotImplementedError(
		        "Abstract method 'get_result_set' not implemented")

	def write_to_db(self):
		raise NotImplementedError(
		        "Abstract method 'write_to_db' not implemented")
