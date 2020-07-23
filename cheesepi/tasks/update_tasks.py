from __future__ import unicode_literals
import os
import sys
import argparse
from time import time
from builtins import str

ENABLED = False
try:
    from twisted.internet import defer
    from twisted.internet import reactor
    from txmsgpackrpc.client import connect
    ENABLED = True
except ImportError:
    print("Error: Can not import Twisted framework, CheesePi code updating is disabled...")
    raise

import cheesepi as cheesepi
from cheesepi.tasks.task import Task

logger = cheesepi.config.get_logger(__name__)

SERVER_PORT = 18080

class Updatetasks(Task):
    """Inform the central server that we are alive"""

    # construct the process and perform pre-work
    def __init__(self, dao, spec):
        Task.__init__(self, dao, spec)
        self.spec['taskname'] = "updatetasks"
        if 'server' not in spec:
            self.spec['server'] = cheesepi.config.get_controller()

    def run(self):
        logger.info("Getting tasks for ID:{} from {} @ {}, PID: {}".format(
            self.spec['peer_id'], self.spec['server'], time(), os.getpid()))
        tasks = self.get_tasks(self.spec['peer_id'])
        tasks.addCallback(self.act)

    @defer.inlineCallbacks
    def get_tasks(self, peer_id):
        if ENABLED:
            c = yield connect('localhost', SERVER_PORT, connectTimeout=5, waitTimeout=5)
            res = yield c.createRequest('get_tasks', peer_id)
            c.disconnect()
            defer.returnValue(res)

    def act(self,d):
        logger.info(d['result'])


def main(peer_id):
    spec = {'peer_id': int(peer_id)}
    beacon_task = Updatetasks(None, spec)
    beacon_task.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default=None, help='peer id')
    args = parser.parse_args()

    if args.id is None:
        print("Error: missing --id")
        sys.exit()
    if ENABLED:
        reactor.callWhenRunning(main, args.id)
        reactor.run()
    else:
        print("Error: Can not import Twisted framework, updating disabled...")
