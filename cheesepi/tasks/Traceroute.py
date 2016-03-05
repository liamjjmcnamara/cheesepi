import time
import os
import platform
import re

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

class Traceroute(Task.Task):

	def __init__(self, dao, spec={}):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "traceroute"
		if not 'landmark' in self.spec: self.spec['landmark'] = "www.sics.se"

	def run(self):
		logger.info("Tracerouting %s @ %f PID: %d" % (self.spec['landmark'], time.time(), os.getpid()))
		self.measure(self.spec['landmark'])

	def measure(self, landmark):
		#Extract the ethernet MAC address of the PI
		startTime = cp.utils.now()
		output    = self.perform(landmark)
		endTime   = cp.utils.now()
		#trc, hoplist = reformat(tracerouteResult, startTime, endTime)
		logger.debug(output)
		parsed = self.parse(output, startTime, endTime)
		parsed['uploaded']= 8 * 3 * len(parsed['hops'])
		parsed['uploaded']= parsed['downloaded']
		self.insertData(self.dao, parsed['traceroute'], parsed['hops'])

	#Execute traceroute function
	def perform(self, target):
		#traceroute command"
		command = "traceroute %s"%(target)
		self.spec['return_code'], output = self.execute(command)
		if self.spec['return_code']==0:
			return output
		return None

	def parse_null(self, hop_count):
		return {'hop_count': hop_count,
			'domain1': "*", 'domain2': "*", 'domain3': "*",
			'ip1'    : "*", 'ip2'    : "*", 'ip3'    : "*",
			'delay1': -1, 'delay2': -1, 'delay3': -1, }

	#############################
	# Parse Linux command
	#

	def parse(self, data, start_time, end_time):
		ret={}
		lines = data.split("\n")
		ret['traceroute'] = self.parse_destination(lines[0], start_time, end_time)
		hops=[]
		for line in lines[1:-1]:
			hop_count = int(line[:3].strip())
			hops.append(self.parse_hop(hop_count, line[4:]))
		logger.debug("hops: ",hops)
		ret['hops']=hops
		return ret

	def parse_destination(self, destination, start_time, end_time):
		traceroute = {}
		fields = destination.split()
		traceroute['domain']	 = fields[2]
		traceroute['ip']		 = fields[3][1:-1]
		traceroute['start_time'] = start_time
		traceroute['end_time']	 = end_time
		return traceroute

	def parse_hop(self, hop_count, host_line):
		"""This does not yet deal with network problems"""
		hop={'hop_count':hop_count}
		retry="1" # string accumulator
		for match in re.finditer(r"\*|(([\w\.-]+) \(([\d\.]+)\)  ([\d\.ms ]+) )", host_line):
			if match.group(0)=="*": # found a non response
				hop['domain'+retry]="*"
				hop['ip'+retry]="*"
				hop['delay'+retry]="-1"
			else: # some host reploiued N times
				for delay in match.group(4).split("ms"):
					hop['domain'+retry]= match.group(2)
					hop['ip'+retry]    = match.group(3)
					hop['delay'+retry] = delay
					retry = str(int(retry)+1) # inc but keep as string
			retry = str(int(retry)+1) # inc but keep as string
		return hop


	#########################
	## Mac traceroute
	########################
	def parse_mac(self, data):
		hops=[]
		lines = data.split()
		lines.pop(0)
		hop_count=-1
		while (len(lines)>0):
			line = lines.pop(0)
			hop_count = int(line[:3].strip())
			logger.debug(hop_count)
			host_line = line[4:] # extract everything after hopcount
			host_fields = host_line.split()
			if len(host_fields)==3:
				hops.extend(self.parse_null(hop_count))
			elif len(host_fields)==8: # the same host responds for each retry
				hop_entries = self.parse_hop_1host(hop_count,host_fields)
				hops.extend(hop_entries)
			elif len(host_fields)==4: # multiple hosts respond at this hop
				retry2 = lines.pop(0)[4:] #pop the next 2 lines
				retry3 = lines.pop(0)[4:]
				hop_entries = self.parse_hop_3host(hop_count,host_line, retry2, retry3)
				hops.extend(hop_entries)
		logger.debug(hops)
		return hops


	def parse_hop_1host(hop_count, host_fields):
		return {'hop_count': hop_count,
			'domain1': host_fields[0], 'domain2': host_fields[0], 'domain3': host_fields[0],
			'ip1'    : host_fields[1], 'ip2'    : host_fields[1], 'ip3'    : host_fields[1],
			'delay1' : host_fields[2], 'delay2' : host_fields[4], 'delay3' : host_fields[6],
			}

	def parse_hop_3host(hop_count, retry1, retry2, retry3):
		retry1_fields = retry1.split()
		retry2_fields = retry2.split()
		retry3_fields = retry3.split()
		return {'hop_count': hop_count,
			'domain1': retry1_fields[0], 'domain2': retry1_fields[0], 'domain3': retry1_fields[0],
			'ip1'	: retry1_fields[1], 'ip2'	: retry2_fields[1], 'ip3'	: retry3_fields[1],
			'delay1': retry1_fields[2], 'delay2': retry2_fields[2], 'delay3': retry3_fields[2],
			}
	###


	#insert the tracetoute results into the database
	def insertData(self, dao, traceroute, hoplist):
		logger.debug("Writting to the Traceroute table")
		traceroute_id = dao.write_op("traceroute", traceroute)

		for hop in hoplist:
			logger.debug(hop)
			#hop.traceroute = traceroute_id
			hop['traceroute_id'] = traceroute_id
			dao.write_op("traceroute_hop",hop)


#parses arguments
if __name__ == "__main__":
	if platform.system()=="Darwin":
		print "Seems to be Darwin OS (Mac), exiting..."
		exit(0)

	#general logging here? unable to connect etc
	config = cp.config.get_config()
	dao = cp.config.get_dao()

	spec = {'landmark':'www.sics.se'}
	traceroute_task = Traceroute(dao, spec)
	traceroute_task.run()

