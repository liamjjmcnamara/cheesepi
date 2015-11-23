import json


# To be subclassed by explicit measurement tasks
class Task:

    def __init__(self,a,b):
        self.taskname = "Superclass"
    #def __init__(a,b,c):
    #    pass

    def toDict(self):
        return {'taskname':'superclass'}

    def toJson(self):
        return json.dumps(self.toDict())

    # this will be overridden by subclasses
    def run(self):
        print "Task not doing anything..."


