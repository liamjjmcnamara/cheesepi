from __future__ import unicode_literals
import sys
import time
import os

import youtube_dl

sys.path.append("/usr/local/")
import cheesepi.utils
import Task

logger = cheesepi.config.get_logger()

def callback(d):
	print d
	if d['status'] == 'finished':
		print('Done downloading, now converting ...')

class Dash(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname    = "dash"
		self.source      = parameters['source']

	def toDict(self):
		return {'taskname'   :self.taskname,
				'source'     :self.source,
				}

	# actually perform the measurements, no arguments required
	def run(self):
		print "Dash download: %s @ %f, PID: %d" % (self.source, time.time(), os.getpid())
		self.measure()

	# measure and record funtion
	def measure(self):
		start_time = cheesepi.utils.now()
		op_output = self.perform()
		end_time = cheesepi.utils.now()
		#print op_output

		#parsed_output = self.parse_output(op_output, self.source, start_time, end_time)
		#self.dao.write_op(self.taskname, parsed_output)

	def perform(self):
		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
			'logger': logger,
			'progress_hooks': [callback],
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			#ydl.download(['http://www.youtube.com/watch?v=BaW_jenozKc'])
			ydl.download([self.source])

	#read the data from ping and reformat for database entry
	def parse_output(self, data, source, start_time, end_time):
		ret = {}
		ret["source"]      = source
		ret["start_time"]  = start_time
		ret["end_time"]    = end_time

		lines = data.split("\n")
		first_line = lines.pop(0).split()
		return ret

if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	parameters = {'source':'http://www.youtube.com/watch?v=_OBlgSz8sSM'}
	dash_task = Dash(dao, parameters)
	dash_task.run()
