#!/usr/bin/env python

import time
import os
import sched
import multiprocessing

from Ping import Ping
from Traceroute import Traceroute

start_time = time.time()

s = sched.scheduler(time.time, time.sleep)
pool = None # pool must be global, yet instantiated in __main__
pool_size = 5


results = []
def log_result(result):
    results.append(result)


def timestamp(): return (time.time()-start_time)
def print_queue(): print s.queue

# Perform a scheduled Task
def run(task):
    print "\nRunning %s @ %f" % (task.taskname,timestamp())
    pool.apply_async(task.run, args=(1,), callback=log_result)
    #print "async returned"

# Reschedule a cycle of measurements
# Record which cycle, to avoid clock drift
def reschedule(cycle):
    print "Rescheduling cycle %d @ %f" % (cycle,timestamp())

    s.enter(2, 1, run, [Ping("google.com")])
    s.enter(2, 1, run, [Traceroute("google.com")])
    s.enter(6, 1, reschedule, [cycle+1])
    #print_queue()

# Begin the measurement cycles
def initiate():
    print "Start: ", timestamp()
    reschedule(0)
    s.run()
    print "End: ", timestamp()

print "pid: %d" % os.getpid()

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=pool_size)

    initiate()

    pool.close()
    pool.join()

time.sleep(20)

