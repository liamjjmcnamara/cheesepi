from __future__ import unicode_literals
import sys
import os
from time import time
from builtins import str

from txmsgpackrpc.client import connect
from twisted.internet import defer


sys.path.append("/usr/local/")
import Task

SERVER_PORT = 18080

class Beacon(Task.Task):
	"""Inform the central server that we are alive"""

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "beacon"
		self.peer_id   = parameters['peer_id']
		self.server      = "cheesepi.sics.se"
		if 'server' in parameters: self.server = parameters['server']

	def toDict(self):
		return {'taskname'   :self.taskname,
				'cycle'      :self.cycle,
				'peer_id'    :self.peer_id,
				}

	def run(self):
		print "Beaconing ID:%d to %s @ %f, PID: %d" % (self.peer_id, self.server, time(), os.getpid())
		self.beacon(self.peer_id)

	@defer.inlineCallbacks
	def beacon(self, peer_id):
		c = yield connect('localhost', SERVER_PORT, connectTimeout=5, waitTimeout=5)

		res = yield c.createRequest('beacon', peer_id)
		c.disconnect()
		defer.returnValue(res)
		pass


def main(peer_id):
	spec = {'peer_id': int(peer_id)}
	beacon_task = Beacon(None,spec)
	beacon_task.run()


if __name__ == "__main__":
    from twisted.internet import reactor
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default=None,
                        help='peer id')

    args = parser.parse_args()

    if args.id is None:
        exit()
    reactor.callWhenRunning(main, args.id)
    reactor.run()