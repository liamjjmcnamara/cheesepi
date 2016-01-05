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
	logger.info(d)
	if d['status'] == 'finished':
		logger.debug(('Done downloading, now converting ...'))

class Dash(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "dash"
		if not 'source' in spec:
			self.spec['source'] = "http://www.youtube.com/watch?v=_OBlgSz8sSM"

	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("Dash download: %s @ %f, PID: %d" % (self.source, time.time(), os.getpid()))
		self.measure()

	# measure and record funtion
	def measure(self):
		self.spec['start_time'] = cheesepi.utils.now()
		op_output = self.perform()
		self.spec['end_time'] = cheesepi.utils.now()
		logger.debug(op_output)

		#parsed_output = self.parse_output(op_output)
		#self.dao.write_op(self.spec['taskname'], parsed_output)

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
	def parse_output(self, data, ):

		lines = data.split("\n")
		first_line = lines.pop(0).split()
		return self.spec

if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	spec = {'source':'http://www.youtube.com/watch?v=_OBlgSz8sSM'}
	dash_task = Dash(dao, spec)
	dash_task.run()

