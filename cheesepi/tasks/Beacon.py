from __future__ import unicode_literals
import os
from time import time
from builtins import str

from txmsgpackrpc.client import connect
from twisted.internet import defer

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

SERVER_PORT = 18080

class Beacon(Task.Task):
	"""Inform the central server that we are alive"""

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "beacon"
		if not 'server' in spec: self.spec['server'] = cp.config.get_controller()

	def run(self):
		logger.info("Beaconing ID:%d to %s @ %f, PID: %d" % (self.spec['peer_id'], self.spec['server'], time(), os.getpid()))
		self.beacon(self.spec['peer_id'])

	@defer.inlineCallbacks
	def beacon(self, peer_id):
		c = yield connect('localhost', SERVER_PORT, connectTimeout=5, waitTimeout=5)

		res = yield c.createRequest('beacon', peer_id)
		c.disconnect()
		defer.returnValue(res)
		pass


def main(peer_id):
	spec = {}
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
		print "Error: missing --id"
		exit()
	reactor.callWhenRunning(main, args.id)
	reactor.run()
