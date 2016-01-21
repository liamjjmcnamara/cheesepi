import time

import logging
import pymongo
import math

from .dao import DAO
from cheesepilib.exceptions import ServerDaoError, NoSuchPeer

from cheesepilib.server.storage.models.statistics import StatisticsSet

# What is the threshold in seconds to be considered 'active'
ACTIVE_THRESHOLD = 3600

class MongoDAO(DAO):
	log = logging.getLogger("cheesepi.server.storage.MongoDAO")

	def __init__(self):
		self.__init__('localhost', 27017)

	def __init__(self, host, port):
		self.client = pymongo.MongoClient()
		self.db = self.client.cheesepi

		# Initialization stuff
		# This makes sure that the peer_id field is unique and fast lookups can
		# be performed
		self.db.beacons.create_index([("last_seen",pymongo.ASCENDING)])
		self.db.tasks.create_index([("peer_id",pymongo.ASCENDING)])
		self.db.peers.create_index([("peer_id",pymongo.ASCENDING)], unique=True)
		# This (I think) ensures fast lookups for ('peer_id','results.target_id')
		self.db.peers.create_index([("peer_id",pymongo.ASCENDING),
		                            ("results.target_id",pymongo.ASCENDING)])
		self.db.peers.create_index([("peer_id",pymongo.ASCENDING),
		                            ("statistics.target_id",pymongo.ASCENDING)])

	def close(self):
		pass # Nothing to do??

	def get_bulk_writer(self):
		return self.db.peers.initialize_ordered_bulk_op()

	def peer_beacon(self, peer_id, host, last_seen=0):
		if last_seen==0: last_seen=time.time()
		result = self.db.beacons.update_one(
			{'peer_id':peer_id},
			{'$set':{
				'peer_id':peer_id,
				'host':host,
				'last_seen':last_seen,
				}
			},
			upsert=True
		)
		return self._return_status(result.acknowledged)

	def active_peers(self, since=0):
		if since<=0: since=time.time()-ACTIVE_THRESHOLD
		result = self.db.beacons.find({"last_seen": {"$gt": since}})
		return result

	def find_peer(self, peer_id):
		result = self.db.peers.find({'peer_id':peer_id}, limit=1)
		if result.count() > 0:
			return result
		else:
			raise NoSuchPeer()

	def get_peers(self):
		result = self.db.peers.find()
		return result

	def get_random_peer(self):
		from random import randint
		num_peers = self.db.peers.count()
		#print("{} peers in collection".format(num_peers))
		result = self.db.peers.find(limit=1, skip=randint(0,num_peers))
		if result.count() > 0:
			peer = result.next()
			return peer
		else:
			# What does this mean????
			raise ServerDaoError()

	def write_task(self, peer_id, task):
		result = self.db.peers.update(
			{'peer_id':peer_id},
			{'$push': {'tasks':task}}
		)
		return result

	def get_tasks(self, peer_id):
		results = self.db.tasks.find(
			{'peer_id':peer_id},
			projection={'_id':0},
			limit=5 # should be unlimited
		)
		return results

	def register_peer(self, peer_id, host):
		result = self.db.peers.update_one(
			{'peer_id':peer_id},
			{'$set':{
				'peer_id':peer_id,
				'host':host,
				'tasks':[],
				'results':[]
				}
			},
			upsert=True
		)
		return self._return_status(result.acknowledged)

	def write_result(self, peer_id, result):
		# Can probably merge these operations into one???

		# Insert the result in the peers results-list if there is a task with a
		# matching task_id in its tasks-list
		update = self.db.peers.update(
			{
				'peer_id':peer_id,
				#'tasks': {
					#'$elemMatch':{'task_id':result['task_id']}
				#}
			},
			{'$push': {'results':result}},
			upsert=True
		)
		# Remove the task with that task_id
		#remove = self.db.peers.update(
			#{'peer_id':peer_id},
			#{'$pull': {
				#'tasks':{'task_id':result['task_id']}
				#}
			#}
		#)
		return self._return_status(update['updatedExisting'])




	def get_all_stats(self, peer_id):
		return self.get_stats_set_for_targets(peer_id, None)
	def get_stats_set(self, peer_id, target):
		"""
		Returns a StatisticsSet object loaded with all the statistics for
		measurements from peer_id to target.

		Args:
			peer_id: a peer id
			target: a Target object
		Returns:
			A StatisticsSet object if query is successful, None otherwise.
		"""
		return self.get_stats_set_for_targets(peer_id, [target])

	def get_stats_set_for_results(self, peer_id, results):
		"""
		Returns a StatisticsSet object loaded with all the statistics for
		measurements from peer_id to all targets that concern the results in
		the result list.

		Args:
			peer_id: a peer id
			results: a list of Result objects
		Returns:
			A StatisticsSet object if query is successful, None otherwise.
		"""
		targets = [result.get_target() for result in results]

		return self.get_stats_set_for_targets(peer_id, targets)

	def get_stats_set_for_targets(self, peer_id, targets):
		"""
		Returns a StatisticsSet object loaded with all the statistics for
		measurements from peer_id to all targets in the targets list.

		Args:
			peer_id: a peer id
			targets: a list of Target objects
		Returns:
			A StatisticsSet object if query is successful, None otherwise.
		"""

		projection = None

		if targets is not None:
			projection = {}
			for target in targets:
				key = "statistics.{}".format(target.get_uuid())
				projection[key] = 1

		stats = self.db.peers.find(
			{'peer_id':peer_id},
			projection,
		)

		# Should be unique so can only ever find one
		if stats.count() > 0:
			#self.log.info(stats[0])
			return StatisticsSet.fromDict(stats[0]['statistics'])
		else:
			return StatisticsSet()

	def write_stats_set(self, peer_id, statistics_set):
		"""
		Write a statistics set object to the database.

		Args:
			peer_id: a peer id
			statistcs_set: a StatisticsSet object
		Returns:
			the result from the write operation
		"""
		bulk_writer = self.db.peers.initialize_ordered_bulk_op()

		bulk_writer = self.bulk_write_stats_set(bulk_writer, peer_id,
		                                        statistics_set)

		result = bulk_writer.execute()
		self.log.info("Wrote statistics set with result: {}".format(result))
		return result

	def bulk_write_stats_set(self, bulk_writer, peer_id, statistics_set):
		"""
		Queue writing of a StatisticsSet object to a bulk writer object.

		Args:
			bulk_writer: a bulk writer object
			peer_id: a peer id
			statistcs_set: a StatisticsSet object
		Returns:
			the modified bulk writer object
		"""
		#self.log.info("IN WRITE_STATS")

		prefix_key = "statistics" #.format(target.get_uuid())

		stat_object = {}
		#self.log.info(statistics_set)

		for stat in statistics_set:
			stat_target_uuid = stat.get_target().get_uuid()
			#stat_type = stat.get_type()
			#if stat_target_uuid not in stat_object:
				#stat_object[stat_target_uuid] = {}
			#stat_object[stat_target_uuid][stat_type] = stat.toDict()

			key = "{}.{}".format(prefix_key, stat_target_uuid)

			bulk_writer.find(
				{'peer_id':peer_id}
				).upsert(
				).update_one(
				{'$set':{
					key:{
						stat.get_type():stat.toDict(),
						},
					}
				},
			)
		#self.log.info("EXITING WRITE_STATS")

		return bulk_writer

	def write_results(self, peer_id, results):
		"""
		Writes a list of results from a peer to the database.

		Args:
			peer_id: a peer id
			results: a list of Result objects
		Returns:
			the result of the write operation
		"""
		bulk_writer = self.db.peers.initialize_ordered_bulk_op()

		bulk_writer = self.bulk_write_results(bulk_writer, peer_id, results)

		result = bulk_writer.execute()
		self.log.info("Wrote a list of results objects with result: {}".format(result))
		return result

	def bulk_write_results(self, bulk_writer, peer_id, results):
		"""
		Queue writing of a list of Result objects to a bulk writer object.

		Args:
			bulk_writer: a bulk writer object
			peer_id: a peer id
			results: a list of Result objects
		Returns:
			the modified bulk writer object
		"""
		for result in results:
			bulk_writer.find(
				{'peer_id':peer_id}
				).upsert(
				).update(
				{'$push': {'results':result.toDict()}}
			)
		return bulk_writer

	def purge_results(self, peer_id):
		result = self.db.peers.update(
			{'peer_id':peer_id},
			{'results':[]}
		)
		return result

	def purge_results_older_than(self, peer_id, timestamp):
		result = self.db.peers.update(
			{'peer_id':peer_id},
			{'$pull': {
				'results':{
					'timestamp':{'$lt': timestamp}
					}
				}
			}
		)
		return result
