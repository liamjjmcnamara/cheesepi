#!/usr/bin/env python

import time
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
cycle_length = float(config['cycle_length'])
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
	print "\nRunning %s @ %f" % (task.taskname, timestamp())
	#task.run()
	#pool.apply_async(task.run, args=(), callback=log_result)
	pool.apply_async(async, args=[task], callback=log_result)


# Reschedule a cycle of measurements
# Record which cycle, to avoid clock drift
def reschedule(task):
	print "Rescheduling cycle %d @ %f" % (task.cycle, timestamp())

	# reschedule all tasks from the config file
	for t in schedule_list:
		schedule_task(t)

	if repeat_schedule:
		# schedule a task to reschedule all other tasks
		spec = {'cycle': task.cycle+1}
		reschedule_task = cheesepi.tasks.Reschedule(dao, spec)
		s.enter(cycle_length*(task.cycle+1), 1, reschedule, [reschedule_task])
	#print get_queue()

def schedule_task(spec):
	if type(spec) is cheesepi.tasks.Task:
		task = spec # we already have na object
	else: # otherwise build it
		task = cheesepi.tasks.build_task(dao, spec)
	if task == None:
		logger.error("Task specification not valid: "+str(spec))
		return # do nothing
	s.enter(spec['time'], NORMAL, run, [task])

# return list of task objects
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


# Begin the first measurement cycle
def initiate():
	print "Start: ", timestamp()
	spec = {'cycle': 0}
	reschedule_task = cheesepi.tasks.Reschedule(dao, spec)
	reschedule(reschedule_task)
	s.run()
	print "End: ", timestamp()


def load_schedule():
	#try to get from central server
	tasks = cheesepi.config.load_remote_schedule()

	if tasks==None :
		# just use local
		tasks = cheesepi.config.load_local_schedule()
	return tasks


schedule_list = load_schedule()

#print "pid: %d" % os.getpid()
if __name__ == "__main__":
	pool = multiprocessing.Pool(processes=pool_size)

	initiate()
	if pool is not None:
		pool.close()
		pool.join()

time.sleep(3000)

