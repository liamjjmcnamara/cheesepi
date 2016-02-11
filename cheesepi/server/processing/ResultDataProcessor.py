from __future__ import unicode_literals, absolute_import, print_function

import os
import shutil
import logging

from cheesepi.server.parsing.ResultParser import ResultParser
from cheesepi.exceptions import UnsupportedResultType
from .utils import untar, md5_filehash

class ResultDataProcessor(object):
	"""
	Encapsulates file handling and cleanup of processing result data.
	"""
	log = logging.getLogger("cheesepi.server.parsing.ResultDataProcessor")

	def __init__(self, filepath):
		"""
		Object which encapsulates the handling of a result dump received
		by the server. Should be initialized with the absolute path to a
		tar archive with the results.
		"""
		self._extracted = False
		self._filepath = filepath
		self._path = os.path.dirname(filepath)

		self._md5_hash = md5_filehash(filepath)
		self._extract_path = os.path.join(self._path, self._md5_hash)

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

	def get_hash(self):
		return self._md5_hash

	def extract(self):
		#self.log.info("Extracting {} --> {}".format(
		#    self._filepath, self._extract_path))
		untar(self._filepath, self._extract_path)
		self._extracted = True

	def delete_extracted(self):
		if not self._extracted:
			raise Exception("Data not extracted.")

		#self.log.info("Deleting folder {}".format(self._extract_path))
		shutil.rmtree(self._extract_path)
		self._extracted = False

	def process(self):
		if not self._extracted:
			raise Exception("Data not extracted.")

		#self.log.info("Processing files in {}".format(self._extract_path))

		from cheesepi.server.storage.mongo import MongoDAO
		from pprint import pformat

		# Process every file in the extracted folder
		files = [os.path.join(self._extract_path, f)
				for f in os.listdir(self._extract_path)]
		for filename in files:
			try:
				dao = MongoDAO('localhost', 27017)

				#parser = ResultParser.fromFile(filename)
				with ResultParser.fromFile(filename) as parser:
					results = parser.parse()
					#self.log.info("Results {}".format(results))
					peer_id = parser.get_peer_id()
					self.log.info("Peer id {}".format(peer_id))

					stats = dao.get_stats_set_for_results(peer_id, results)
					#self.log.info("Fetched old stats")
					#self.log.info("Fetched:\n{}".format(pformat(stats.toDict())))

					upload_count = dao.get_result_count(peer_id)
					stats.absorb_results(results, upload_index=upload_count+1)
					#self.log.info("\n\nRESULT COUNT = {} for peer {}\n\n".format(result_count, peer_id))
					#self.log.info("Absorbed new results")
					#self.log.info("Absorbed:\n{}".format(pformat(stats.toDict())))

					bulk_writer = dao.get_bulk_writer()

					bulk_writer = dao.bulk_write_stats_set(bulk_writer, peer_id, stats)

					# Write results
					bulk_writer = dao.bulk_write_results(bulk_writer, peer_id, results)

					res = bulk_writer.execute()
					self.log.info("Bulk wrote to database with result: {}".format(res))

					#parser.write_to_db()

					#for result in results:
						#res = dao.write_result(peer_id, result)
						#self.log.info(res)

				#from pprint import PrettyPrinter
				#printer = PrettyPrinter(indent=2)
				#printer.pprint(output)

			except UnsupportedResultType as e:
				# TODO This suppresses the full stack trace for the moment, but
				# should be removed once all parsers have been implemented. This
				# is here to declutter the log while developing
				self.log.warn("{}".format(e))
			except Exception as e:
				self.log.exception("Error parsing file {}".format(filename))
			finally:
				dao.close()

	def delete(self):
		"""
		We're done, delete all files.
		"""
		#self.log.info("Deleting file {}".format(self._filepath))
		os.remove(self._filepath)
