#!/usr/bin/env python

import sys
import tarfile
import json

import cheesepi as cp

def slurp_file(dao, series, fd):
	"""Read a file into the 'series' database"""
	content = fd.read()
	points = json.loads(content)
	dao.slurp(series, points)

def slurp_database(dao, filename):
	"""Read a tgz filename into the database"""
	tar = tarfile.open(filename)
	for member in tar.getmembers():
		series_name = member.name[:-5] # trim '.json'
		print series_name
		fd=tar.extractfile(member)
		slurp_file(dao, series_name, fd)

	tar.close()

def usage():
	print "Usage: %s <Dump .tgz file>" % sys.argv[0]
	sys.exit(1)

if __name__ == "__main__":
	dao = cp.config.get_dao()

	if len(sys.argv)!=2:
		usage()
	else:
		filename = sys.argv[1]
		slurp_database(dao, filename)
