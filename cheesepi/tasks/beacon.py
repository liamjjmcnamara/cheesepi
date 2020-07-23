import argparse
import os
from time import time
from builtins import str

ENABLED = False
try:
    from twisted.internet import defer
    from twisted.internet import reactor
    from txmsgpackrpc.client import connect
    ENABLED = True
except ImportError as exception:
    # twisted import failed
    print("Error: Can not import Twisted/messagepack framework, Beaconing disabled...")
    raise # re-raise the problem

import cheesepi
from cheesepi.tasks.task import Task

LOGGER = cheesepi.config.get_logger(__name__)
SERVER_PORT = 18080

class Beacon(Task):
    """Inform the central server that we are alive"""

    # construct the process and perform pre-work
    def __init__(self, dao, spec):
        Task.__init__(self, dao, spec)
        self.spec['taskname'] = "beacon"
        if not 'server' in spec:
            self.spec['server'] = cp.config.get_controller()

    def run(self):
        LOGGER.info("Beaconing ID: %d to %s @ %f, PID: %d", self.spec['peer_id'],
                    self.spec['server'], time(), os.getpid())
        self.beacon(self.spec['peer_id'])

    @defer.inlineCallbacks
    def beacon(self, peer_id):
        if ENABLED:
            con = yield connect('localhost', SERVER_PORT, connectTimeout=5, waitTimeout=5)
            res = yield con.createRequest('beacon', peer_id)
            con.disconnect()
            defer.returnValue(res)


def main(peer_id):
    spec = {}
    beacon_task = Beacon(None,spec)
    beacon_task.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default=None, help='peer id')
    args = parser.parse_args()

    if args.id is None:
        print("Error: missing --id")
        exit()
    if ENABLED:
        reactor.callWhenRunning(main, args.id)
        reactor.run()
    else:
        print("Error: Can not import Twisted framework, beaconing disabled.")
