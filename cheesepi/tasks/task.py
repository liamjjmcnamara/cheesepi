import random
import json
from subprocess import Popen, PIPE

import cheesepi as cp

# To be subclassed by explicit measurement tasks
class Task:

    def __init__(self, dao=None, spec={}):
        self.dao = dao
        self.spec = {}
        self.spec['offset'] = 0
        self.spec['period'] = 86400 # 24hrs
        self.spec['uploaded'] = 1 # bytes, placeholder
        self.spec['taskname'] = "Superclass"
        self.spec['inititator'] = cp.utils.get_host_id()
        self.spec['downloaded'] = 1 # bytes, placeholder
        # overwrite defauls:
        for key in spec.keys():
            self.spec[key] = spec[key]

        # allow random offsets
        if self.spec['offset'] == "rand":
            self.spec['offset'] = random.randint(1, self.spec['period']-1)

    def to_dict(self):
        return self.spec

    def to_json(self):
        return json.dumps(self.to_dict())

    def execute(self, program):
        result = Popen(program, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        result.stdout.flush()
        output = result.stdout.read()
        print(output)
        result.poll() # set return code
        return result.returncode, output

    # this will be overridden by subclasses
    def run(self):
        print("Task not doing anything...")
