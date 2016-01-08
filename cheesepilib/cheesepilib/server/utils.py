from __future__ import unicode_literals, absolute_import, print_function

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
	log.info("Starting server on port %d..." % args.port)
	reactor.run()
