from __future__ import unicode_literals, absolute_import, print_function


import os
import tarfile
import hashlib
import json

# Processing functions, untar, calculating stats etc...
# TODO some kind of logging??
# How do we know where the database is???

def process_upload(uploaded_file):
	# Find out the hash of the file
	hasher = hashlib.md5()
	with open(uploaded_file) as fd:
		hasher.update(fd.read())
	md5_hash = hasher.hexdigest()

	# Use hash as destination folder name
	path = os.path.dirname(uploaded_file)
	destination = os.path.join(path, md5_hash)

	untar(uploaded_file, destination)

	process_data(destination)

def process_data(directory):
	files = [os.path.join(directory, f) for f in os.listdir(directory)]
	for filename in files:
		with open(filename) as fd:
			json_obj = json.load(fd)
		#from pprint import PrettyPrinter
		#printer = PrettyPrinter(indent=2)
		#printer.pprint(json_obj)
		taskname = get_taskname(json_obj)
		print("name: {}".format(taskname))

		if taskname == 'ping':
			parser = PingResultParser(json_obj)
			output = parser.parse()
			print(output)

def untar(filename, destination):
	with tarfile.open(filename) as tar:
		tar.extractall(destination)

# PARSING JSON OBJECT STUFF (SHOULD PROBABLY GO IN ANOTHER MODULE)

class ResultParser(object):

	def parse(self):
		raise NotImplementedError("Abstract method 'parse' not implemented")

class PingResultParser(ResultParser):

	# Takes an object parsed from json
	def __init__(self, obj):
		self.obj = obj

	def parse(self):
		"""
		Here we should try to parse all the data we're interested in,
		and handle any resulting errors in a sane way. Should ALWAYS
		return an output that can be directly inserted into the database.
		"""
		return "output"

def get_taskname(obj):
	return obj[0]['series'][0]['name']
