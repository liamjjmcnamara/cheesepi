
# To be subclassed by explicit measurement tasks
class Task:

    def __init__(self):
        self.taskname = "Superclass"

    def record(self):
        pass

    # this will be overridden by subclasses
    def run(self):
        print "Task not doing anything..."

