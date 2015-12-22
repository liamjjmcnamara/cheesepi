#!/usr/bin/env python

import time
import math
import sys
import sched
import multiprocessing
import logging

import cheesepi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

start_time = time.time()

dao    = cheesepi.config.get_dao()
config = cheesepi.config.get_config()

# Create scheduler object, use 'real' time
s = sched.scheduler(time.time, time.sleep)
repeat_schedule = True # keep rescheuling?
# list of tasks to perform each schedule (populate later)
schedule_list = []

pool = None # pool must be global, yet instantiated in __main__
pool_size = 5

# Task priority
IMPORTANT  = 1
NORMAL     = 2

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
	print "\nRunning %s @ %f" % (task.spec['taskname'], timestamp())
	pool.apply_async(async, args=[task], callback=log_result)


def schedule_task(spec):
	print spec
	if type(spec) is cheesepi.tasks.Task:
		task = spec # we already have an object
	else: # otherwise build it
		task = cheesepi.tasks.build_task(dao, spec)

	if task == None:
		logger.error("Task specification not valid: "+str(spec))
		return # do nothing

	next_period = 1 + math.floor(time.time() / task.spec['period'])
	#	round(time.time() - (time.time() % 3600))
	abs_start = (next_period*task.spec['period']) + task.spec['offset']
	delay = abs_start-time.time()
	print "Timme %d %f %f" % (next_period,abs_start,delay)
	s.enter(delay, NORMAL, run, [task])

# return list of queued task objects
def get_queue():
	q=[]
	for t in s.queue:
		start_time = t.time
		# extract the dict of the first parameter to the event
		#print t
		spec = t.argument[0].toDict()
		spec['start_time'] = start_time
		q.append(spec)
	return q

def load_schedule():
	#try to get from central server
	tasks = cheesepi.config.load_remote_schedule()
	if tasks==None:
		# just use local
		tasks = cheesepi.config.load_local_schedule()
	return tasks


schedule_list = load_schedule()

#print "pid: %d" % os.getpid()
if __name__ == "__main__":
	pool = multiprocessing.Pool(processes=pool_size)

	# reschedule all tasks from the config file
	for t in schedule_list:
		schedule_task(t)
	#print get_queue()

	if pool is not None:
		pool.close()
		pool.join()


