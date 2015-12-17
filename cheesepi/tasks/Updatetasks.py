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

class Updatetasks(Task.Task):
	"""Inform the central server that we are alive"""

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "updatetasks"
		self.server      = "cheesepi.sics.se"
		if 'server' in parameters: self.server = parameters['server']

	def toDict(self):
		return {'taskname'   :self.taskname,
				'cycle'      :self.cycle,
				}

	def run(self):
		print "Beaconing to %s @ %f, PID: %d" % (self.server, time(), os.getpid())
		self.beacon(234)

	@defer.inlineCallbacks
	def beacon(self, peer_id):
		c = yield connect('localhost', SERVER_PORT, connectTimeout=5, waitTimeout=5)

		res = yield c.createRequest('updatetasks', peer_id)
		c.disconnect()
		defer.returnValue(res)
		pass


def main(client_id):
	spec = {id: client_id}
	beacon_task = Updatetasks(None,spec)
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
