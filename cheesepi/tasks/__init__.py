
from Task import Task
from Ping import Ping
from Httping import Httping
from Traceroute import Traceroute

import json

def build_json(dao, json_str):
	spec = json.loads(json_str)
	return build_task(spec)

def build_task(dao, spec):
	if spec['taskname']=='ping':
		return Ping(dao, spec)
	if spec['taskname']=='httping':
		return Httping(dao, spec)
	if spec['taskname']=='traceroute':
		return Traceroute(dao, spec)
	else:
		raise Exception('Task name not specified!')

