import time
import os

from Task import Task

class Traceroute(Task):

    def __init__(self, dao, parameters):
        self.taskname = "traceroute"
        self.dao = dao
        self.landmark = parameters['landmark']

    def run(self):
        print "Tracerouting: %s" % self.landmark
        print "pid: %d" % os.getpid()

        time.sleep(4)

