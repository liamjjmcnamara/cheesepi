from __future__ import unicode_literals, absolute_import, print_function

import logging
import sys

from zope.interface import provider
from twisted.logger import ILogObserver, formatEvent

@provider(ILogObserver)
class PrintingObserver:
	def __call__(self, event):
		print("[{level}] {text}".format(
			level=event['log_level'].name.upper(),
			text=formatEvent(event)))

### Script entrypoints

def start_control_server():
	import argparse

	from twisted.internet import reactor
	from twisted.logger import Logger, globalLogPublisher

	from cheesepilib.server.control import (CheeseRPCServerFactory,
	                                        CheeseRPCServer)
	from cheesepilib.server.storage.mongo import MongoDAO

	# Argument parsing
	parser = argparse.ArgumentParser()
	parser.add_argument('--port', type=int, default=18080,
	                    help='Port to listen on')
	args = parser.parse_args()

	# Logging
	log = Logger()
	globalLogPublisher.addObserver(PrintingObserver())

	dao = MongoDAO()
	control_server = CheeseRPCServer(dao).getStreamFactory(CheeseRPCServerFactory)

	reactor.listenTCP(args.port, control_server)
	log.info("Starting control server on port %d..." % args.port)
	reactor.run()

def init_logging(level=logging.INFO, stdout=True):
	# Python Logging
	logging.basicConfig()
	logging.root.setLevel(logging.INFO)

	# Write logs to stdout
	if stdout:
		out_handler = logging.StreamHandler(sys.stdout)
		formatter = logging.Formatter('[%(levelname)s][%(name)s]: %(message)s')
		out_handler.setFormatter(formatter)
		logging.root.addHandler(out_handler)


def start_upload_server():
	import argparse

	from twisted.internet import reactor
	from twisted.logger import Logger, globalLogPublisher, STDLibLogObserver
	from twisted.web.server import Site
	from twisted.web.resource import Resource

	from cheesepilib.server.upload import UploadHandler

	# Argument parsing
	parser = argparse.ArgumentParser()
	parser.add_argument('--port', type=int, default=18090,
	                    help='Port to listen on')
	args = parser.parse_args()

	init_logging()

	# Make twisted logging write to pythons logging module
	globalLogPublisher.addObserver(STDLibLogObserver(name="cheesepi.server.upload"))

	# Use twisted logger when in twisted
	log = Logger()

	root = Resource()
	root.putChild("upload", UploadHandler())
	upload_server = Site(root)

	reactor.listenTCP(args.port, upload_server)
	log.info("Starting upload server on port %d..." % args.port)
	reactor.run()
