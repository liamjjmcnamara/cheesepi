#!/usr/bin/env python

import os
import sys
import time
import math
import signal
import traceback
import multiprocessing
import logging
from sched import scheduler

import cheesepi
import cheesepi.storage

start_time = time.time()

logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
logger = cheesepi.config.get_logger(__name__)
config = cheesepi.config.get_config()
dao = cheesepi.storage.get_dao()

# Create scheduler object, use 'real' time
s = scheduler(time.time, time.sleep)
REPEAT_SCHEDULE = True # keep rescheuling?
# list of tasks to perform each schedule (populate later)
schedule_list = []

pool = None # pool must be global, yet instantiated in __main__
pool_size = 5 # max number of concurrent tasks...

# Task priority
IMPORTANT = 1
NORMAL = 2

def log_result(result):
    #logging.info("Task callback() result..."+str(result))
    pass

def timestamp():
    return (time.time() - start_time)

def print_queue():
    logger.debug(s.queue)

# Need to catch Ctrl+C, and so wrap the Interupt as an Exception
def asynchronous(task):
    """Wrapper around asynchronous task execution"""
    try:
        task.run()
    except KeyboardInterrupt:
        pass # probably just user destruction
    except:
        cls, exc, tb = sys.exc_info()
        if issubclass(cls, Exception):
            raise # No worries, pass up the stack
        # Need to wrap the exception with something multiprocessing will recognise
        print("Unhandled exception {} ({}):\n{}".format(cls.__name__, exc, traceback.format_exc()))
        logger.error("Unhandled exception {} ({}):\n{}".format((cls.__name__, exc, traceback.format_exc())))
        raise Exception("Unhandled exception: {} ({})".format((cls.__name__, exc)))

# Perform a scheduled Task, and schedule the next
def run(task, spec):
    """Run this task asychronously, and schedule the next period"""
    pool.apply_async(asynchronous, args=[task], callback=log_result)
    if REPEAT_SCHEDULE:
        schedule_task(spec)


def schedule_task(spec):
    """Ensure task defiend by specificaiton is executed"""
    task = cheesepi.utils.build_task(dao, spec)
    print("task: "+str(task))
    if task is None:
        logger.error("Task specification not valid: " + str(spec))
        return

    if task.spec['period'] == 0:
        return # dummy task
    next_period = 1 + math.floor(time.time() / task.spec['period'])
    abs_start = (next_period*task.spec['period']) + task.spec['offset']
    delay = abs_start - time.time()
    # queue up a task, include spec for next period
    s.enter(delay, NORMAL, run, [task, spec])

def get_queue():
    """return list of queued task objects"""
    que = []
    for task in s.queue:
        # extract the dict of the first parameter to the event
        spec = task.argument[0].to_dict()
        spec['start_time'] = task.time
        que.append(spec)
    return que

def load_schedule():
    """Load a schedule of task specifications"""
    #try to get from central server
    tasks = None # cheesepi.config.load_remote_schedule()
    if tasks is None:
        # just use local
        tasks = cheesepi.config.load_local_schedule()
    if cheesepi.config.get("auto_upgrade"):
        upgrade_period = 86400 # 24hrs
        task_str = {'taskname':'upgradecode', 'period':upgrade_period, 'offset':'rand'}
        tasks.append(task_str)
    return tasks

def print_schedule(schedule_list):
    print("Using the following schedule:")
    for task in schedule_list:
        print(task)

def HUP():
    """Reload config if we receive a HUP signal"""
    global pool
    print("Reloading...")
    pool.terminate()
    start()

def start():
    global pool
    schedule_list = load_schedule()
    print_schedule(schedule_list)
    pool = multiprocessing.Pool(processes=pool_size)
    cheesepi.utils.make_series()
    # reschedule all tasks from the schedule specified in config file
    for task in schedule_list:
        schedule_task(task)

    print("Reloading...")
    try:
        s.run()
    except KeyboardInterrupt:
        pass

    if pool is not None:
        pool.close()
        pool.join()

    # wait for the longest time between tasks
    max_period = 10000
    time.sleep(max_period)


def stop():
    pass

if __name__ == "__main__":
    logger.info("Dispatcher PID: %d".format(os.getpid()))

    # register HUP signal catcher
    signal.signal(signal.SIGHUP, HUP)

    start()

