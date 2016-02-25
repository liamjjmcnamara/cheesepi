import time
import os
import tarfile
import tempfile
import StringIO
import requests
import sys
import argparse

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)


class Upload(Task.Task):
	"""Task to upload data to central server.
	Upload and local file storage are not controllable through the spec.
	If called programatically, we always want remote upload, and no file accumulation"""
	# construct the process and perform pre-work
	def __init__(self, dao, spec={}):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "upload"
		if not 'collector' in self.spec: # no special endpoint
			if not 'server' in self.spec: self.spec['server'] = cp.config.get_controller()
			self.spec['collector'] = self.spec['server']+"/upload.py"

	def run(self):
		"""Upload data server, may take some time..."""
		logger.info("Uploading data... @ %f, PID: %d" % (time.time(), os.getpid()))

		self.dump_db()

	def dump_db(self, upload=True, store_file=False, last_dumped=None):
		if last_dumped==None:
			last_dumped = cp.config.get_last_dumped(self.dao)
		if last_dumped==-1:
			logger.info("Never dumped this DB...")
		else:
			logger.info("Last dumped DB: "+str(last_dumped))
		print "Last dumped DB: "+str(last_dumped)

		dumped_tables = self.dao.dump(last_dumped)
		logger.debug(dumped_tables)
		ethmac = cp.utils.getCurrMAC()
		parameters = {'ethmac': ethmac}

		fd=None
		if store_file:
			filename=str(int(time.time()))
			fd = open(filename+".tgz",'w')
		else:
			# make a temp file that disappears outside of scope
			fd = tempfile.TemporaryFile()

		# make a zipfile object with this file handle
		tar = tarfile.open(fileobj=fd, mode="w:gz")

		for table in dumped_tables.keys():
			#print table
			table_info = tarfile.TarInfo(name=table+".json")
			table_info.size=len(dumped_tables[table])
			tar.addfile(table_info, StringIO.StringIO(dumped_tables[table]))
		tar.close()
		fd.flush()
		fd.seek(0) # flush and reset file handle, so it can be read for POST

		if upload:
			files = {'file': ('archive.tgz', fd), }
			try:
				r = requests.post("http://"+self.spec['collector'], data=parameters, files=files)
				logger.debug("Uploaded, with response: "+r.text)
				print "Uploaded, with response: "+r.text
				cp.config.set_last_dumped() # record that we successfully dumped
				return r.text
			except:
				logger.error("Failed to upload data dump")
		return None



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Dump CheesePi DB, to local file or remote server')

	parser.add_argument('--no-upload',  dest='upload', action='store_false')
	parser.add_argument('--store-file', dest='store_file', action='store_true')
	parser.add_argument('--since', metavar='s', type=int, nargs='?', default=None, help="Dump all data since time s")
	parser.set_defaults(upload=True)
	parser.set_defaults(store_file=False)
	args = parser.parse_args()

	dao = cp.config.get_dao()
	dump_task = Upload(dao)
	dump_task.dump_db(args.upload, args.store_file, args.since)

