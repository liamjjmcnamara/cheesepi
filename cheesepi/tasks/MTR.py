import time
import os

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

class MTR(Task.Task):

	def __init__(self, dao, spec={}):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "traceroute"
		if not 'landmark' in self.spec: self.spec['landmark'] = "www.sics.se"

	def run(self):
		logger.info("MTRing %s @ %f PID: %d" % (self.spec['landmark'], time.time(), os.getpid()))
		self.measure(self.spec['landmark'])

	def measure(self, landmark):
		#Extract the ethernet MAC address of the PI
		startTime = cp.utils.now()
		output    = self.perform(landmark)
		endTime   = cp.utils.now()

		logger.debug(output)
		hops = self.parse(output, startTime, endTime)
		self.insertData(self.dao, hops)

	#Execute traceroute function
	def perform(self, target, count=10):
		#traceroute command"
		command = "mtr  --report-wide -c%d %s"%(count,target)
		self.spec['return_code'], output = self.execute(command)
		if self.spec['return_code']==0:
			return output
		return None

	def parse(self, data, start_time, end_time):
		self.spec['start'] = start_time
		self.spec['end']   = end_time
		#print data
		lines = data.split("\n")
		hops=[]
		for line in lines[2:-1]:
			#print line
			fields = line.split()
			hops.append(self.parse_hop(fields))
		#logger.debug("hops: ",hops)
		self.spec['hopcount']=len(hops)
		self.spec['uploaded']= 64*8 * self.spec['hopcount']
		return hops

	def parse_hop(self, fields):
		ret={}
		ret['hop']   = int(fields[0][:-4])
		ret['host']  = fields[1]
		ret['loss']  = float(fields[2][:-1])
		ret['mean']  = float(fields[5])
		ret['stdev'] = float(fields[8])
		ret['min']   = float(fields[6])
		ret['max']   = float(fields[7])
		return ret



	#insert the mtr results into the database
	def insertData(self, dao, hoplist):
		logger.debug("Writting to the MTR table")
		mtr_id = dao.write_op("mtr", self.spec)

		for hop in hoplist:
			logger.debug(hop)
			hop['mtr_id'] = mtr_id
			dao.write_op("mtr_hop",hop)


#parses arguments
if __name__ == "__main__":

	#general logging here? unable to connect etc
	config = cp.config.get_config()
	dao = cp.config.get_dao()

	spec = {'landmark':'www.sics.se'}
	mtr_task = MTR(dao, spec)
	mtr_task.run()

