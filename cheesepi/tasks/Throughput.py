import sys
import time
import os

sys.path.append("/usr/local/")
import cheesepi.utils
import Task

# https://github.com/sivel/speedtest-cli
import speedtest

class Throughput(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "throughput"

	def toDict(self):
		return {'taskname'   :self.taskname,
			}

	# actually perform the measurements, no arguments required
	def run(self):
		print "Speedtest throughput: @ %f, PID: %d" % (time.time(), os.getpid())
		self.measure()

	# measure and record funtion
	def measure(self):
		start_time = cheesepi.utils.now()
		op_output = speedtest.speedtest()
		end_time = cheesepi.utils.now()
		#print op_output

		parsed_output = self.parse_output(op_output, start_time, end_time)
		self.dao.write_op(self.taskname, parsed_output)

	#read the data and reformat for database entry
	def parse_output(self, data, start_time, end_time):
		ret = {}
		ret['download'] = data['download']
		ret['upload']   = data['upload']
		ret['serverid'] = data['serverid']
		ret['ping']     = data['ping']
		return ret

if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	parameters = {}
	throughput_task = Throughput(dao, parameters)
	throughput_task.run()
