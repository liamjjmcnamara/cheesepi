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
		self._peer_id = None

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
		from pprint import pformat
		columns = inp[0]['series'][0]['columns']
		#self.log.info("\n{}".format(pformat(columns)))

		entries = [entry for entry in inp[0]['series'][0]['values']]
		for entry in entries:
			peer_id = self._peer_id = entry[columns.index('peer_id')]
			if self._peer_id is None:
				self._peer_id = peer_id
			elif self._peer_id != peer_id:
				raise Exception(
					"Found inconsistent peer_id: {}, expected: {}".format(
						peer_id, self._peer_id)
				)
			# TODO this is done because the sequence is stored as a string
			# representation of a list, should be changed in the future so that
			# it's a list from the start
			import ast
			delay_sequence = ast.literal_eval(entry[columns.index('delays')])

			landmark = entry[columns.index('landmark')]
			target_id = entry[columns.index('target_id')]

			target = {}

			if landmark is None and target_id is not None:
				target['type'] = 'peer'
				target['ip'] = entry[columns.index('destination_address')]
				target['uuid'] = entry[columns.index('target_id')]
				target['port'] = '80' # TODO not in data
			elif landmark is not None:
				target['type'] = 'landmark'
				target['ip'] = entry[columns.index('destination_address')]
				target['domain'] = entry[columns.index('landmark')]
				target['port'] = '80' # TODO not in data

			db_entry = {
				'task_name':'ping',
				'start_time':entry[columns.index('start_time')],
				'end_time':entry[columns.index('end_time')],
				'target': target,
				'value': {
					# This is where the actual results go
					'delay_sequence':delay_sequence,
					'probe_count':entry[columns.index('ping_count')],
					'packet_loss':entry[columns.index('packet_loss')],
					'packet_size':entry[columns.index('packet_size')],
					'max_rtt':entry[columns.index('maximum_RTT')],
					'min_rtt':entry[columns.index('minimum_RTT')],
					'avg_rtt':entry[columns.index('average_RTT')],
					'stddev_rtt':entry[columns.index('stddev_RTT')],
				},
			}

			# TODO
			from cheesepilib.server.storage.models.result import Result
			from pprint import pformat
			# TODO first argument should be peer_id
			r = Result.fromDict(1, db_entry)
			result_objects.append(r)
			#self.log.info(pformat(r.toDict()))
			# TODO

			results.append(db_entry)

		# TODO
		#from cheesepilib.server.storage.models.statistics import StatisticsSet
		#from cheesepilib.server.storage.models.target import LandmarkTarget
		#from cheesepilib.server.storage.models.PingStatistics import PingStatistics
		#dao = MongoDAO('localhost', 27017)
		#target = LandmarkTarget("127.0.0.1", 80, "sics.se")
		#stats_set = dao.get_stats_set(1, target)
		#if stats_set is None:
			#stats_set = StatisticsSet([PingStatistics(target)])
		#self.log.info("PRINTING STATISTICS SET MODEL")
		#self.log.info(pformat(stats_set.toDict()))
		#stats_set.absorb_results(result_objects)
		#self.log.info("RESULTS ABSORBED, PRINTING AGAIN")
		#self.log.info(pformat(stats_set.toDict()))
		#tmp = dao.write_stats_set(1, stats_set)
		# TODO

		self._result_objects = result_objects

		self._result_set = results
		self._parsed = True

		return result_objects

	def get_result_set(self):
		return self._result_set

	def get_peer_id(self):
		return self._peer_id

	def write_to_db(self):
		if len(self._result_set) == 0:
			raise Exception("No results parsed.")

		# TODO This should be configured via config file
		dao = MongoDAO('localhost', 27017)

		#status = dao.write_ping_results(1, "sics.se", self._result_set)
		status = dao.write_results(1, self._result_objects)
		self.log.info("Database write returned {}".format(status))

