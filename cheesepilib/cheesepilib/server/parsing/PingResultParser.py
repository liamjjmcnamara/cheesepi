from __future__ import unicode_literals, absolute_import, print_function

import logging

from .ResultParser import ResultParser

from cheesepilib.server.storage.mongo import MongoDAO

class PingResultParser(ResultParser):
	log = logging.getLogger("cheesepi.server.parsing.PingResultParser")

	# Takes an object parsed from json
	def __init__(self, obj):
		self._parsed = False
		self._input_obj = obj
		self._result_set = []

	def __enter__(self):
		self.parse()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass

	def parse(self):
		"""
		Here we should try to parse all the data we're interested in,
		and handle any resulting errors in a sane way. Should ALWAYS
		return an output that can be directly inserted into the database.
		"""
		inp = self._input_obj
		results = []
		result_objects = []

		# TODO WHAT ABOUT PEER_ID????

		entries = [entry for entry in inp[0]['series'][0]['values']]
		for entry in entries:
			# TODO this is done because the sequence is stored as a string
			# representation of a list, should be changed in the future so that
			# it's a list from the start
			import ast
			delay_sequence = ast.literal_eval(entry[2])

			db_entry = {
				'task_name':'ping',
				'start_time':entry[17],
				'end_time':entry[6],
				'target': {
					'type':'landmark', # TODO This should be dynamic
					'ip':entry[3],
					'domain':entry[4],
					'port':'80', # TODO not in data
				},
				'value': {
					# This is where the actual results go
					'delay_sequence':delay_sequence,
					'probe_count':entry[14],
					'packet_loss':entry[11],
					'packet_size':entry[12],
					'max_rtt':entry[8],
					'min_rtt':entry[9],
					'avg_rtt':entry[20],
					'stddev_rtt':entry[18],
				},
			}

			# TODO
			from cheesepilib.server.storage.models.result import Result
			from pprint import pformat
			r = Result.fromDict(db_entry)
			result_objects.append(r)
			self.log.info(pformat(r.toDict()))
			# TODO

			results.append(db_entry)

		# TODO
		from cheesepilib.server.storage.models.statistics import StatisticsSet
		from cheesepilib.server.storage.models.target import LandmarkTarget
		from cheesepilib.server.storage.models.PingStatistics import PingStatistics
		dao = MongoDAO('localhost', 27017)
		target = LandmarkTarget("127.0.0.1", 80, "sics.se")
		stats = dao.get_stats_set(1, target)
		if stats is not None:
			self.log.info(stats)
			stat_set = StatisticsSet.fromDict(stats)
		else:
			stat_set = StatisticsSet(target, {'ping':PingStatistics(target)})
		self.log.info("PRINTING STATISTICS SET MODEL")
		self.log.info(pformat(stat_set.toDict()))
		stat_set.absorb_results(result_objects)
		self.log.info("RESULTS ABSORBED, PRINTING AGAIN")
		self.log.info(pformat(stat_set.toDict()))
		tmp = dao.write_stats_set(1, target, stat_set)
		# TODO

		self._result_objects = result_objects

		self._result_set = results
		self._parsed = True
	
	def get_result_set():
		return self._result_set

	def write_to_db(self):
		if len(self._result_set) == 0:
			raise Exception("No results parsed.")

		# TODO This should be configured via config file
		dao = MongoDAO('localhost', 27017)

		#status = dao.write_ping_results(1, "sics.se", self._result_set)
		status = dao.write_results(1, self._result_objects)
		self.log.info("Database write returned {}".format(status))

