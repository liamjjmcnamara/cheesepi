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
	from twisted.internet import reactor
	from twisted.logger import Logger, globalLogPublisher

	from cheesepilib.server.control import (CheeseRPCServerFactory,
	                                        CheeseRPCServer)
	from cheesepilib.server.storage.mongo import MongoDAO

	SERVER_PORT = 18080

	log = Logger()
	globalLogPublisher.addObserver(PrintingObserver())

	dao = MongoDAO()

	control_server = CheeseRPCServer(dao).getStreamFactory(CheeseRPCServerFactory)

	reactor.listenTCP(SERVER_PORT, control_server)
	log.info("Starting server on port %d..." % SERVER_PORT)
	reactor.run()
