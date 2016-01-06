
import json

from Task import Task
from Dummy import Dummy
from Status import Status
from Reschedule import Reschedule
from Ping import Ping
from Httping import Httping
from Traceroute import Traceroute
from Dash import Dash
from DNS import DNS
from Throughput import Throughput
from iPerf import iPerf
from Beacon import Beacon
from Upload import Upload


def _build_json(dao, json_str):
	spec = json.loads(json_str)
	return build_task(spec)

def _build_task(dao, spec):
	if not 'taskname' in spec:
		return None

	if spec['taskname']=='ping':
		return Ping(dao, spec)
	elif spec['taskname']=='httping':
		return Httping(dao, spec)
	elif spec['taskname']=='traceroute':
		return Traceroute(dao, spec)
	elif spec['taskname']=='dash':
		return Dash(dao, spec)
	elif spec['taskname']=='dns':
		return DNS(dao, spec)
	elif spec['taskname']=='throughput':
		return Throughput(dao, spec)
	elif spec['taskname']=='iperf':
		return iPerf(dao, spec)
	elif spec['taskname']=='beacon':
		return Beacon(dao, spec)
	elif spec['taskname']=='upload':
		return Upload(dao, spec)
	elif spec['taskname']=='status':
		return Status(dao, spec)
	elif spec['taskname']=='dummy':
		return Dummy(dao, spec)
	else:
		raise Exception('Task name not specified! '+str(spec))

