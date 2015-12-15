
from Task import Task
from Reschedule import Reschedule
from Ping import Ping
from Httping import Httping
from Traceroute import Traceroute
from DASH import DASH
from DNS import DNS
from Throughput import Throughput
from iPerf import iPerf

import json

def build_json(dao, json_str):
	spec = json.loads(json_str)
	return build_task(spec)

def build_task(dao, spec):
	if not 'taskname' in spec:
		return None
	elif not 'time' in spec:
		return None
	elif spec['taskname']=='ping':
		return Ping(dao, spec)
	elif spec['taskname']=='httping':
		return Httping(dao, spec)
	elif spec['taskname']=='traceroute':
		return Traceroute(dao, spec)
	elif spec['taskname']=='dash':
		return DASH(dao, spec)
	elif spec['taskname']=='dns':
		return DNS(dao, spec)
	elif spec['taskname']=='throughput':
		return Throughput(dao, spec)
	elif spec['taskname']=='iperf':
		return iPerf(dao, spec)
	else:
		raise Exception('Task name not specified! '+spec)

