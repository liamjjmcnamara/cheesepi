from __future__ import print_function, absolute_import

from twisted.internet import reactor
from twisted.logger import Logger, globalLogPublisher

from cheeselib.logger import PrintingObserver
from cheeselib.server.rpc import CheeseRPCServerFactory, CheeseRPCServer
from cheeselib.server.storage.mongo import MongoDAO

SERVER_PORT = 18080

log = Logger()

globalLogPublisher.addObserver(PrintingObserver())

dao = MongoDAO()

rpc_server = CheeseRPCServer(dao).getStreamFactory(CheeseRPCServerFactory)

reactor.listenTCP(SERVER_PORT, rpc_server)
log.info("Starting server on port %d..." % SERVER_PORT)
reactor.run()
