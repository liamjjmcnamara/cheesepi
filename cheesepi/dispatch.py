#!/usr/bin/env python

import time
import os
import signal
import sys
import sched
import multiprocessing

import cheesepi

start_time = time.time()

s = sched.scheduler(time.time, time.sleep)
pool = None # pool must be global, yet instantiated in __main__
pool_size = 5

dao    = cheesepi.config.get_dao()
config = cheesepi.config.get_config()

# Ctrl doesnt work well with multiprocessing.py
# http://noswap.com/blog/python-multiprocessing-keyboardinterrupt
def signal_handler(signal, frame):
    print('Ctrl+C!')
    # kill children
    if pool!=None:
        pool.terminate()
        pool.join()

    sys.exit(0)
#signal.signal(signal.SIGINT, signal_handler)


results = []
def log_result(result):
    print "logging result..."
    results.append(result)
def timestamp(): return (time.time()-start_time)
def print_queue(): print s.queue

# Need to catch Ctrl+C, and so wrap the Interupt as an Exception
def async(task):
    try:
        task.run()
    except:
        cls, exc, tb = sys.exc_info()
        if issubclass(cls, Exception):
            raise # No worries
        # Need to wrap the exception with something multiprocessing will recognise
        import traceback
        print "Unhandled exception %s (%s):\n%s" % (cls.__name__, exc, traceback.format_exc())
        raise Exception("Unhandled exception: %s (%s)" % (cls.__name__, exc))

# Perform a scheduled Task
def run(task):
    print "\nRunning %s @ %f" % (task.taskname, timestamp())
    #task.run()
    #pool.apply_async(task.run, args=(), callback=log_result)
    pool.apply_async(async, args=[task], callback=log_result)

# Reschedule a cycle of measurements
# Record which cycle, to avoid clock drift
def reschedule(cycle):
    print "Rescheduling cycle %d @ %f" % (cycle, timestamp())

    params1 = {'landmark':'google.com'}
    s.enter(1, 1, run, [cheesepi.tasks.Ping(dao, params1)])
    params2 = {'landmark':'facebook.com'}
    s.enter(1, 1, run, [cheesepi.tasks.Traceroute(dao, params2)])
    #s.enter(6, 1, reschedule, [cycle+1])
    #print_queue()

# Begin the measurement cycles
def initiate():
    print "Start: ", timestamp()
    reschedule(0)
    s.run()
    print "End: ", timestamp()

print "pid: %d" % os.getpid()

# To called by pool process on init, ignore SIGNALs
def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=pool_size)

    try:
        initiate()
    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating workers"
        pool.terminate()
        pool.join()
    else:
        pool.close()
        pool.join()

time.sleep(20)

