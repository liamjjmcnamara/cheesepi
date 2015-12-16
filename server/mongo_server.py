from __future__ import print_function

from builtins import str

from txmsgpackrpc.server import MsgpackRPCServer
from txmsgpackrpc.factory import MsgpackServerFactory

from zope.interface import provider
from twisted.logger import Logger, ILogObserver
from twisted.internet import defer

from server_dao.mongo import MongoDAO

@provider(ILogObserver)
class PrintingObserver:
    def __call__(self, event):
        print("[{level}] {text}".format(level=event['log_level'].name.upper(),
                                        text=formatEvent(event)))

class MongoRPCServerFactory(MsgpackServerFactory):
    """
    Overrides MsgpackServerFactory
    """
    log = Logger()

    def buildProtocol(self, addr):
        p = self.protocol(self, sendErrors=False) # Override to False
        return p

class MongoRPCServer(MsgpackRPCServer):
    log = Logger()

    def _error(self, error):
        import traceback
        self.log.error("{error}\n{traceback}",
                       error=error, traceback=traceback.format_exc(error))
    def __init__(self):
        self.dao = MongoDAO()

    def remote_hello(self, add=None):
        self.log.info("received request for hello, add is {add}", add=add)
        return "world"

    @defer.inlineCallbacks
    def remote_register(self, peer_id):
        try:
            self.log.info("peer with id {peer_id} registering", peer_id=peer_id)
            result = yield self.dao.register_peer({
                'peer_id':peer_id,
                'tasks':[],
                'results':[]
            })
            #self.log.info("inserted with result: {result}",result=result)
            defer.returnValue(result)
        except Exception as e:
            self._error(e)
            defer.returnValue("fail")

    @defer.inlineCallbacks
    def remote_upload_result(self, data):
        try:
            find = yield self.dao.find_peer(data['peer_id'])
            #self.log.info("{result} {count}", result=find[0], count=find.count())
            update = yield self.dao.write_result(data['peer_id'], data['result'])
            defer.returnValue(update['status'])
        except Exception as e:
            self._error(e)
            defer.returnValue("fail")

    @defer.inlineCallbacks
    def remote_get_tasks(self, peer_id):
        try:
            tasks = yield self.dao.get_tasks(peer_id)
            #self.log.info("got tasks {tasks}", tasks=tasks)
            defer.returnValue(tasks)
        except Exception as e:
            self._error(e)
            defer.returnValue("fail")


class DataMuncher(object):
    log = Logger()

    def __init__(self):
        from twisted.internet import reactor, task

        self.dao = MongoDAO()

        self.tasks = [
                (task.LoopingCall(self.purge_old_results), 15),
                (task.LoopingCall(self.delegate_tasks), 10)
        ]

    def register(self):
        """ start tasks """
        for task in self.tasks:
            task[0].start(task[1])

    @defer.inlineCallbacks
    def delegate_tasks(self):
        from random import randint
        peers = yield self.dao.get_peers()

        for peer in peers:
            self.log.info("Delegating tasks for peer {peer}", peer=peer['peer_id'])
            target = yield self.dao.get_random_peer()
            #self.log.info("target is {target}", target=target)
            if target is not None and peer['peer_id'] != target['peer_id']:
                #self.log.info("found target {target}", target=target['peer_id'])
                task = {
                    'task_name':'ping',
                    'task_id':randint(0,99999), # placeholder
                    'target_id':target['peer_id']
                }
                self.log.info("New task {} ".format(task['task_id']) +
                              "for {}: ".format(peer['peer_id']) +
                              "ping to {}".format(task['target_id']))
                result = yield self.dao.write_task(peer['peer_id'], task)

    @defer.inlineCallbacks
    def purge_old_results(self):
        from time import time
        limit = time() - (30) # 30s ago

        self.log.info("Starting purge")
        peers = yield self.dao.get_peers()
        for peer in peers:
            self.log.info("purging results of peer {peer}", peer=peer['peer_id'])
            result = yield self.dao.purge_results_older_than(peer['peer_id'], limit)
            #self.log.info("{result}", result=result)


if __name__ == "__main__":
    log = Logger()

    from twisted.internet import reactor
    from twisted.logger import formatEvent, globalLogPublisher

    globalLogPublisher.addObserver(PrintingObserver())

    server = MongoRPCServer().getStreamFactory(MongoRPCServerFactory)

    muncher = DataMuncher()
    muncher.register()

    reactor.listenTCP(18080, server)
    log.info("starting on port 18080")
    reactor.run()
