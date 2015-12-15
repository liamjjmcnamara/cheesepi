import sys
import time
import os
import re
import subprocess

sys.path.append("/usr/local/")
import cheesepi.utils
import cheesepi.config
import Task

class Wifi(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters={}):
		Task.Task.__init__(self, dao, parameters)
		self.taskname	 = "wifi"
		self.config		 = cheesepi.config.get_config()
		self.interface	 = self.config['wlan']

	def toDict(self):
		return {'taskname'	 :self.taskname,
				}

	# actually perform the measurements, no arguments required
	def run(self):
		print "Wifi scan @ %f, PID: %d" % (time.time(), os.getpid())
		self.measure()


	def measure(self):
		start_time = cheesepi.utils.now()
		op_output  = self.perform()
		end_time   = cheesepi.utils.now()
		#print op_output
		parsed_output = self.parse_output(op_output, start_time, end_time)
		#print parsed_output
		scan_digest = self.digest_scan(parsed_output, start_time, end_time)
		self.dao.write_op("wifi_scan", scan_digest)
		for ap in parsed_output:
			dao.write_op("wifi_ap", ap)

	def perform(self):
		try:
			scan_output = subprocess.check_output(["iwlist", self.interface, "scanning"])
		except Exception as e:
			print "Error: iwlist does not seem to run: "+str(e)
			sys.exit(1)
		if "Interface doesn't support scanning" in scan_output:
			print "Error: Interface doesn't support scanning"
			sys.exit(1)
		#print scan_output
		return scan_output

	def parse_output(self, text, start_time, end_time):
		rv=[]
		aps=text.split("Cell")
		aps.pop(0) # remove first
		for ap in aps: # over each AccessPoint
			#print ap
			ap=self.parse_ap(ap)
			ap["start_time"] = start_time
			rv.append(ap)
		return rv

	def parse_ap(self, text):
		ap={}
		try:
			ap['ESSID']   = re.findall('ESSID:".*"', text)[0][7:-1]
		except:
			ap['ESSID']   = "" # No broadcast ESSID
		ap['channel'] = int(re.findall('Channel .*', text)[0][8:-1])
		ap['address'] = re.findall('Address: .*',text)[0][9:]
		try:
			ap['quality'] = int(re.findall('Quality=.*? ', text)[0][8:-5])
			ap['signal']  = int(re.findall('Signal level=.*',text)[0][13:-6])
		except:
			ap['quality'] = -1
			ap['signal']  = -1
		#print ap
		return ap


	def digest_scan(self, aps, start_time, end_time):
		digest={}
		digest["start_time"] = start_time
		digest["end_time"]	 = end_time

		channels = [0]*14 # number of WiFi channels
		# count channel presence
		for ap in aps:
			if ap['channel']<15: # only 2.4Ghz
				channels[ap['channel']] += 1
		for c in xrange(len(channels)):
			digest["channel"+str(c)] = channels[c]
		return digest


	def aps_to_JSON(self, aps, start_time):
		values=[]
		for ap in aps:
			values.append([start_time, ap['ESSID'], ap['channel'], ap['address'], ap['quality'], ap['signal']])

		json = [{ "name" : "ap",
				"columns" : ["time","ESSID","channel","address","quality","signal"],
				"points" : values,
		}]
		return json



if __name__ == "__main__":
	# claim a database storage object
	dao = cheesepi.config.get_dao()
	wifi_task = Wifi(dao)

	scanForever=False
	if scanForever:
		while(True):
			wifi_task.run()
			time.sleep(300)
	else:
		wifi_task.run()

