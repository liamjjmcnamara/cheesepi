import time
import os

import cheesepi
import cheesepi.log
import cheesepi.tasks
from cheesepi.tasks.task import Task

logger = cheesepi.log.get_logger(__name__)

class Dummy(Task):

    # construct the process and perform pre-work
    def __init__(self, dao, spec):
        cheesepi.tasks.task.Task.__init__(self, dao, spec)
        self.spec['taskname'] = "dummy"
        if 'message' not in self.spec:
            self.spec['message'] = "This is not a test"

    # actually perform the measurements, no arguments required
    def run(self):
        logger.info("Dummy: %s @ %f, PID:%s ", self.spec['message'], time.time(), os.getpid())

if __name__ == "__main__":
    #general logging here? unable to connect etc
    dao = cheesepi.storage.get_dao()

    spec = {}
    dummy_task = Dummy(dao, spec)
    dummy_task.run()
