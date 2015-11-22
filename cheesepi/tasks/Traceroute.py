import time
import os

from Task import Task

class Traceroute(Task):

    def __init__(self,domain):
        self.taskname = "traceroute"
        self.domain   = domain

    def run(self):
        print "Tracerouting: %s" % self.domain
        print "pid: %d" % os.getpid()

        time.sleep(4)

