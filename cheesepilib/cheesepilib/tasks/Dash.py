import time
import os

import youtube_dl

import cheesepilib as cp
import Task

logger = cp.config.get_logger()


class Dash(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "dash"
		if not 'source' in spec:
			self.spec['source'] = "http://www.youtube.com/watch?v=_OBlgSz8sSM"
		print self.spec

	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("Dash download: %s @ %f, PID: %d" % (self.spec['source'], time.time(), os.getpid()))
		self.measure()

	# measure and record funtion
	def measure(self):
		self.spec['start_time'] = cp.utils.now()
		self.perform()
		self.spec['end_time'] = cp.utils.now()
		#print "Output: %s" % op_output
		#logger.debug(op_output)
		self.dao.write_op(self.spec['taskname'], self.spec)

	def perform(self):
		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
			'logger': logger,
			'progress_hooks': [self.callback],
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			try:
				ydl.download([self.spec['source']])
			except Exception as e:
				logger.error("Problem with Dash download: "+str(e))
				#self.spec['status'] = "error"
				pass

	def callback(self, stats):
		#logger.info(stats)
		if stats['status'] == 'finished':
			logger.debug('Done downloading, now converting ...')
			#print stats
			if 'downloaded_bytes' in stats:
				self.spec['downloaded'] = stats['downloaded_bytes']
				if 'elapsed' in stats:
					self.spec['download_speed'] = stats['total_bytes'] / stats['elapsed']
			try:
				# avoid cluttering the filesystem
				#os.remove(stats['filename'])
				pass
			except Exception as e:
				logger.error("Problem removing Dash.py Youtube file %s: %s" % (stats['filename'], str(e)))


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cp.config.get_dao()

	spec = {'source':'http://www.youtube.com/watch?v=_OBlgSz8sSM'}
	dash_task = Dash(dao, spec)
	dash_task.run()

