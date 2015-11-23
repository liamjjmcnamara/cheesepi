import json

import cheesepi

# To be subclassed by explicit measurement tasks
class Task:

    def __init__(self):
        self.taskname = "Superclass"

    def toDict(self):
        return {'taskname':'superclass'}

    def toJson(self):
        return json.dumps(self.toDict())

    # this will be overridden by subclasses
    def run(self):
        print "Task not doing anything..."


def build_json(dao, json_str):
    spec = json.loads(json_str)
    return build_task(spec)

def build_task(dao, spec):
    if spec['taskname']=='ping':
        return cheesepi.tasks.Ping(dao, spec)
    if spec['taskname']=='httping':
        return cheesepi.tasks.Httping(dao, spec)
    if spec['taskname']=='traceroute':
        return cheesepi.tasks.Tradceroute(dao, spec)
    else:
        raise Exception('Task name not specified!')
