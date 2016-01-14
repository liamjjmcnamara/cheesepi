import time

import logging
import pymongo
import math

from .dao import DAO
from cheesepilib.exceptions import ServerDaoError, NoSuchPeer

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




	def get_stats_set(self, peer_id, target):
		target_hash = target.get_hash()
		projection = "statistics.{}".format(target_hash)

		stats = self.db.peers.find(
			{'peer_id':peer_id},
			{projection:1},
		)

		# Should be unique so can only ever find one
		if stats.count() > 0:
			return stats[0]['statistics'][target_hash]
		else:
			return None

	def write_stats_set(self, peer_id, target, statistics_set):
		bulk_writer = self.db.peers.initialize_ordered_bulk_op()

		bulk_writer = self.bulk_write_stats_set(bulk_writer, peer_id,
		                                    target, statistics_set)

		result = bulk_writer.execute()
		self.log.info(result)
		return result

	def bulk_write_stats_set(self, bulk_writer, peer_id, target, statistics_set):
		"""
		Write a statistics set object to the database.
		"""
		self.log.info("IN WRITE_STATS")

		prefix_key = "statistics" #.format(target.get_hash())

		stat_object = {}

		for stat in statistics_set:
			stat_target_hash = stat.get_target_hash()
			stat_type = stat.get_type()
			if stat_target_hash not in stat_object:
				stat_object[stat_target_hash] = {'target':target.toDict()}
			stat_object[stat_target_hash][stat_type] = stat.toDict()

		bulk_writer.find(
			{'peer_id':peer_id}
			).upsert(
			).update_one(
			{'$set':{prefix_key:stat_object}}
		)
		self.log.info("EXITING WRITE_STATS")

		return bulk_writer

	def write_results(self, peer_id, results):
		bulk_writer = self.db.peers.initialize_ordered_bulk_op()

		bulk_writer = self.bulk_write_results(bulk_writer, peer_id, results)

		result = bulk_writer.execute()
		self.log.info(result)
		return result

	def bulk_write_results(self, bulk_writer, peer_id, results):
		"""
		Bulk writes a list of result objects
		"""
		for result in results:
			bulk_writer.find(
				{'peer_id':peer_id}
				).upsert(
				).update(
				{'$push': {'results':result.toDict()}}
			)
		return bulk_writer

	#############
	# DEPRECATED#
	#############
	def write_ping_results(self, peer_id, target_id, results):

		from cheesepilib.server.processing.utils import StatObject, median

		# PLACEHOLDER FOR TESTING add peer to database if peer does not exist
		try:
			self.find_peer(peer_id)
		except NoSuchPeer as e:
			self.log.info("No such peer, inserting...")
			self.db.peers.insert({'peer_id':peer_id})

		# Get previous statistics
		stats = self.get_stats(peer_id, target_id)

		from pprint import pformat
		self.log.info("got stats object:\n{}\n".format(pformat(stats)))

		if stats is None:
			# No previous stats for this target, add an entry into the list
			self.db.peers.update_one(
				{'peer_id':peer_id},
				{'$push':{
					'statistics':{'target_id':target_id}}
				}
			)
			mean_delay = StatObject(0,0)
			average_median_delay = StatObject(0,0)
			average_packet_loss = StatObject(0,0)
		else:
			mean_delay = StatObject.fromDict(stats['ping']['mean_delay'])
			average_median_delay = StatObject.fromDict(stats['ping']['average_median_delay'])
			average_packet_loss = StatObject.fromDict(stats['ping']['average_packet_loss'])


		# Bulk write operation object
		bulk_writer = self.db.peers.initialize_ordered_bulk_op()

		probe_count = 0
		packet_loss = 0
		max_rtt = 0
		min_rtt = 999999999
		avg_rtt = 0

		# Main loop which calculates new stats
		for result in results:
			probe_count = probe_count + result['value']['probe_count']
			packet_loss = packet_loss + result['value']['packet_loss']
			max_rtt = max(max_rtt, result['value']['max_rtt'])
			min_rtt = min(min_rtt, result['value']['min_rtt'])
			avg_rtt = result['value']['avg_rtt']

			delay_sequence = result['value']['delay_sequence']

			# Increment the stat counters
			mean_delay.add_datum(avg_rtt)
			average_median_delay.add_datum(median(delay_sequence))
			average_packet_loss.add_datum(packet_loss/probe_count)

			bulk_writer.find(
				{'peer_id':peer_id}
				).upsert(
				).update(
				{'$push': {'results':result}}
			)


		# Find the element in the statistics array for the peer where the
		# target id matches, then update the stats accordingly
		bulk_writer.find(
			{'peer_id':peer_id,
			 'statistics.target_id':target_id}
			).upsert(
			).update_one(
			{'$inc':{
				'statistics.$.ping.total_probe_count':probe_count,
				'statistics.$.ping.total_packet_loss':packet_loss
				},
			 '$max':{'statistics.$.ping.all_time_max_rtt':max_rtt},
			 '$min':{'statistics.$.ping.all_time_min_rtt':min_rtt},
			 '$set':{
				'statistics.$.ping.task_name':'ping',
				'statistics.$.ping.mean_delay.mean':mean_delay._mean,
				'statistics.$.ping.mean_delay.variance':mean_delay._variance,
				'statistics.$.ping.mean_delay.std_dev':mean_delay._std_dev,
				'statistics.$.ping.average_median_delay.mean':average_median_delay._mean,
				'statistics.$.ping.average_median_delay.variance':average_median_delay._variance,
				'statistics.$.ping.average_median_delay.std_dev':average_median_delay._std_dev,
				'statistics.$.ping.average_packet_loss.mean':average_packet_loss._mean,
				'statistics.$.ping.average_packet_loss.variance':average_packet_loss._variance,
				'statistics.$.ping.average_packet_loss.std_dev':average_packet_loss._std_dev,
				},
			}
		)

		update_result = bulk_writer.execute()

		return self._return_status(update_result['nModified']>0)

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
