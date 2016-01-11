from __future__ import unicode_literals, absolute_import, print_function

import os
import hashlib
import shutil

from cheesepilib.server.parsing.ResultParser import ResultParser
from .utils import untar

class ResultDataProcessor(object):

	def __init__(self, filepath):
		"""
		Object which encapsulates the handling of a result dump received
		by the server. Should be initialized with the absolute path to a
		tar archive with the results.
		"""
		self.extracted = False
		self.filepath = filepath
		self.path = os.path.dirname(filepath)

		hasher = hashlib.md5()
		with open(filepath) as fd:
			hasher.update(fd.read())
		self.md5_hash = hasher.hexdigest()
		self.extract_path = os.path.join(self.path, self.md5_hash)

	def __enter__(self):
		"""
		Extract archive.
		"""
		self.extract()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		"""
		Cleanup extracted files and delete the original tar archive.
		"""
		self.delete_extracted()
		self.delete()
		os.listdir(self.path)

	def get_hash(self):
		return self.md5_hash

	def extract(self):
		untar(self.filepath, self.extract_path)
		self.extracted = True

	def delete_extracted(self):
		if not self.extracted:
			raise Exception("Data not extracted.")

		shutil.rmtree(self.extract_path)
		self.extracted = False

	def process(self):
		if not self.extracted:
			raise Exception("Data not extracted.")

		# Process every file in the extracted folder
		files = [os.path.join(self.extract_path, f)
				for f in os.listdir(self.extract_path)]
		for filename in files:
			try:
				parser = ResultParser.fromFile(filename)
				output = parser.parse()

				from pprint import PrettyPrinter
				printer = PrettyPrinter(indent=2)
				printer.pprint(output)

				parser.write_to_db()
			except Exception as e:
				print(e)

	def delete(self):
		"""
		We're done, delete all files.
		"""
		os.remove(self.filepath)
