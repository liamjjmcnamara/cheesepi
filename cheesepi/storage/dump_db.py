#!/usr/bin/env python

import time
import tarfile
import StringIO
import requests

import cheesepi as cp

dump_url = "http://cheesepi.sics.se/upload.py"


def perform_database_dump(since=None):
	dao = cp.config.get_dao()
	# make a temp file that dies on running out of scope
	filename = "cheesepi-%d.tgz" % int(time.time())
	print filename

	if since==None:
		since = cp.config.get_last_dumped(dao)
		print "Last dumped: "+str(since)

	dumped_tables = dao.dump(since)
	ethmac = cp.utils.getCurrMAC()
	parameters = {'ethmac': ethmac}

	fd = open(filename, 'w')
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

	upload=False
	if (upload):
		files = {'file': ('archive.tgz', fd), }
		r = requests.post(dump_url, data=parameters, files=files)
		print r.text
		fd.close()
		# remember when we last successfully dumped our data
		cp.config.set_last_dumped()


if __name__ == "__main__":
	perform_database_dump()
