from __future__ import unicode_literals, absolute_import, print_function

from .ResultParser import ResultParser

from cheesepilib.server.storage.mongo import MongoDAO

class PingResultParser(ResultParser):

	# Takes an object parsed from json
	def __init__(self, obj):
		self.input_obj = obj
		self.output_obj = None

	def parse(self):
		"""
		Here we should try to parse all the data we're interested in,
		and handle any resulting errors in a sane way. Should ALWAYS
		return an output that can be directly inserted into the database.
		"""
		inp = self.input_obj
		out = []

		entries = [entry for entry in inp[0]['series'][0]['values']]
		for entry in entries:
			db_entry = {
				'task_name':'ping',
				'timestamp':entry[0], # TODO should maybe be in unix epoch
				'target': {
					'type':'landmark', # TODO This should be dynamic
					'ip':entry[4],
					'domain':entry[5],
					'port':'80', # TODO not in data
				},
				'value': {
					# This is where the actual results go
					'delay_sequence':entry[2],
					'probe_count':entry[14],
					'packet_loss':entry[11],
					'packet_size':entry[12],
					'max_rtt':entry[8],
					'min_rtt':entry[9],
					'avg_rtt':entry[20],
					'stddev_rtt':entry[18],
				},
			}

			out.append(db_entry)

		self.output_obj = out
		return out

	def write_to_db(self):
		if self.output_obj is None:
			raise Exception("No object parsed.")

		# TODO This should be configured via config file
		dao = MongoDAO('localhost', 27017)
		print(dao.get_peers()[0])
