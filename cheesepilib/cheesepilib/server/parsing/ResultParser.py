from __future__ import unicode_literals, absolute_import, print_function

import json

class ResultParser(object):

	@staticmethod
	def fromFile(filename):
		with open(filename) as fd:
			json_obj = json.load(fd)
		return ResultParser.fromJson(json_obj)

	@staticmethod
	def fromJson(json_obj):
		from .PingResultParser import PingResultParser

		name = ResultParser.get_taskname(json_obj)

		if name == 'ping': return PingResultParser(json_obj)
		else: raise Exception("Unknown task type '{}'.".format(name))

	@staticmethod
	def get_taskname(obj):
		return obj[0]['series'][0]['name']

	def parse(self):
		raise NotImplementedError(
		        "Abstract method 'parse' not implemented")

	def write_to_db(self):
		raise NotImplementedError(
		        "Abstract method 'write_to_db' not implemented")
