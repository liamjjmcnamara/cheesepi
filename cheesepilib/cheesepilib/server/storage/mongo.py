import time

import pymongo

from .dao import DAO
from cheesepilib.exceptions import ServerDaoError, NoSuchPeer

# What is the threshold in seconds to be considered 'active'
ACTIVE_THRESHOLD = 3600

class MongoDAO(DAO):

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

    def write_ping_results(self, peer_id, target_id, results):
        stats = self.db.peers.find({
                'peer_id':peer_id,
                'statistics.target_id':target_id
            },
        )

        if stats.count() > 0:
            print("found existing statistics")
        else:
            # No previous stats
            self.db.peers.insert(
                    {'peer_id':peer_id,
                     'statistics':[{'target_id':target_id}]}
            )

        probe_count = 0
        packet_loss = 0
        max_rtt = 0
        min_rtt = 0
        for result in results:
            probe_count = probe_count + result['value']['probe_count']
            packet_loss = packet_loss + result['value']['packet_loss']
            max_rtt = max_rtt + result['value']['max_rtt']
            min_rtt = min_rtt + result['value']['min_rtt']
            update = self.db.peers.update(
                    {
                        'peer_id':peer_id,
                    },
                    {'$push': {'results':result}},
                    upsert=True
            )


        # Find the element in the statistics array for the peer where the
        # target id matches, then update the stats accordingly
        self.db.peers.update_one(
                {'peer_id':peer_id,
                 'statistics.target_id':target_id
                },
                {'$inc':{
                    'statistics.$.ping.total_probe_count':probe_count,
                    'statistics.$.ping.total_packet_loss':packet_loss
                    },
                 '$max':{'statistics.$.ping.max_rtt':max_rtt},
                 '$min':{'statistics.$.ping.min_rtt':min_rtt},
                },
                upsert=True
        )

        return "bla"

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

