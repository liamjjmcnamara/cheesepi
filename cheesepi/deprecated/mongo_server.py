from __future__ import print_function, absolute_import

from time import time
from txmsgpackrpc.server import MsgpackRPCServer
from txmsgpackrpc.factory import MsgpackServerFactory

from zope.interface import provider
from twisted.logger import Logger, ILogObserver
from twisted.internet import defer

from server_dao.mongo import MongoDAO
from server_dao.exception import NoSuchPeer


SERVER_PORT = 18080

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

    def getRemoteMethod(self, protocol, methodName):
        # This is how you can get the ip address of the peer...
        # Maybe something ugly can be made so that it's passed to the method
        # when needed, like remote_register
        if methodName == 'beacon':
            # When registering we want to know from which ip address the peer
            # is connecting and so we patch the function with an extra parameter
            host = protocol.transport.getPeer().host
            base_function = getattr(self.handler, "remote_" + methodName)
            mod_function = lambda *args: base_function(host, *args)
            return mod_function
        elif methodName == 'register':
            # When registering we want to know from which ip address the peer
            # is connecting and so we patch the function with an extra parameter
            host = protocol.transport.getPeer().host
            base_function = getattr(self.handler, "remote_" + methodName)
            mod_function = lambda *args: base_function(host, *args)
            return mod_function
        else:
            return getattr(self.handler, "remote_" + methodName)

class MongoRPCServer(MsgpackRPCServer):
    log = Logger()

    def _error(self, error):
        import traceback
        self.log.error("{error}\n{traceback}",
                       error=error, traceback=traceback.format_exc(error))
    def __init__(self):
        self.dao = MongoDAO()

    def _response(self, status, body):
        if status == True:
            return {'status':'success','result':body}
        else:
            return {'status':'failure','error':body}

    @defer.inlineCallbacks
    def remote_beacon(self, host, peer_id):
        """
        This remote method gets special handling in getRemoteMethod() in the
        MongoRPCServerFactory class and thus receives the ip of the connecting
        peer
        """
        try:
            self.log.info("peer with id {peer_id} beaconed from host {host}",
                          peer_id=peer_id, host=host)
            result = yield self.dao.peer_beacon(peer_id, host, int(time()))
            self.log.info("beacon with result: {result}",result=result)
            defer.returnValue(self._response(True, result))
        except Exception as e:
            self._error(e)
            defer.returnValue(self._response(False, "error"))

    @defer.inlineCallbacks
    def remote_register(self, host, peer_id):
        """
        This remote method gets special handling in getRemoteMethod() in the
        MongoRPCServerFactory class and thus receives the ip of the connecting
        peer
        """
        try:
            self.log.info("peer with id {peer_id} registering from host {host}",
                          peer_id=peer_id, host=host)
            result = yield self.dao.register_peer(peer_id, host)
            #self.log.info("register with result: {result}",result=result)
            defer.returnValue(self._response(True, result))
        except Exception as e:
            self._error(e)
            defer.returnValue(self._response(False, "error"))


    @defer.inlineCallbacks
    def remote_get_active(self, peer_id):
        try:
            peers = yield self.dao.active_peers()
            defer.returnValue(self._response(True, peers))
        except Exception as e:
            self._error(e)
            defer.returnValue(self._response(False, "error"))

    @defer.inlineCallbacks
    def remote_get_tasks(self, peer_id):
        try:
            # no valid task generation yet...
            tasks = yield self.dao.get_tasks(peer_id)
            task_str=""
            for t in tasks:
                task_str += str(t)
            self.log.info("got tasks {tasks}", tasks=task_str)
            defer.returnValue(self._response(True, task_str))
        except NoSuchPeer as e:
            defer.returnValue(self._response(False, "nosuchpeer"))
        except Exception as e:
            self._error(e)
            defer.returnValue(self._response(False, "error"))


    @defer.inlineCallbacks
    def remote_upload_result(self, data):
        try:
            find = yield self.dao.find_peer(data['peer_id'])
            #self.log.info("{result} {count}", result=find[0], count=find.count())
            update = yield self.dao.write_result(data['peer_id'], data['result'])
            if update['status'] == 'success':
                defer.returnValue(self._response(True, update['status']))
            else:
                defer.returnValue(self._response(False, "Failed to upload."))
        except Exception as e:
            self._error(e)
            defer.returnValue(self._response(False, "error"))

class DataMuncher(object):
    log = Logger()

    def __init__(self):
        self.dao = MongoDAO()
        #from twisted.internet import task
        #self.tasks = [
        #        (task.LoopingCall(self.purge_old_results), 15),
        #        (task.LoopingCall(self.delegate_tasks), 10)
        #]

    def register(self):
        """ start tasks """
        pass
        #for task in self.tasks:
        #    task[0].start(task[1])

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
                    'target_id':target['peer_id'],
                    'target_host':target['host']
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

    rpc_server = MongoRPCServer().getStreamFactory(MongoRPCServerFactory)

    muncher = DataMuncher()
    muncher.register()

    reactor.listenTCP(SERVER_PORT, rpc_server)
    log.info("Starting server on port %d..." % SERVER_PORT)
    reactor.run()
