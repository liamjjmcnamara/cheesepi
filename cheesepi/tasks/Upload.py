import sys
import time
import os
import tarfile
import tempfile
import StringIO
import requests

sys.path.append("/usr/local/")
import cheesepi
import Task

dump_url = "http://cheesepi.sics.se/upload.py"

class Upload(Task.Task):
	"""Task to upload data to central server"""
	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "upload"
		if not 'server' in spec: self.spec['server'] = cheesepi.config.get_controller()

	def run(self):
		"""Upload data server, may take some time..."""
		print "Uploading data... @ %f, PID: %d" % (time.time(), os.getpid())


	def perform_database_dump(self):
		last_dumped = cheesepi.config.get_last_dumped(self.dao)
		print "Last dumped: "+str(last_dumped)
		dumped_tables = self.dao.dump(last_dumped)
		ethmac = cheesepi.utils.getCurrMAC()
		parameters = {'ethmac': ethmac}

		# make a temp file that dies on running out of scope
		fd = tempfile.TemporaryFile()
		# make a zipfile object with this file handle
		tar = tarfile.open(fileobj=fd, mode="w:gz")
		for table in dumped_tables.keys():
			print table
			table_info = tarfile.TarInfo(name=table+".json")
			table_info.size=len(dumped_tables[table])
			tar.addfile(table_info, StringIO.StringIO(dumped_tables[table]))
		tar.close()
		fd.flush()
		fd.seek(0) # flush and reset file handle, so it can be read for POST

		files = {'file': ('archive.tgz', fd), }
		r = requests.post(dump_url, data=parameters, files=files)
		print r.text
		#fd.close()
		# remember when we last successfully dumped our data
		cheesepi.config.set_last_dumped()
		return r.text


if __name__ == "__main__":
	dump_task = Upload()
	dump_task.perform_database_dump()

