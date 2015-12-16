from __future__ import print_function, unicode_literals
import sys
import os
from time import time
from builtins import str

from txmsgpackrpc.client import connect
from twisted.internet import defer


sys.path.append("/usr/local/")
import Task

class Beacon(Task.Task):
	"""Inform the central server that we are alive"""

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "beacon"
		self.server      = "cheesepi.sics.se"
		if 'server' in parameters: self.server = parameters['server']

	def toDict(self):
		return {'taskname'   :self.taskname,
				'cycle'      :self.cycle,
				}

	def run(self):
		print "Beaconing to %s @ %f, PID: %d" % (self.server, time(), os.getpid())
		self.beacon()

	def beacon(self):
		pass



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
