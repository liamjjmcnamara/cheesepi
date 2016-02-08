from __future__ import unicode_literals, absolute_import, print_function

from time import time

from txmsgpackrpc.server import MsgpackRPCServer
from txmsgpackrpc.factory import MsgpackServerFactory

from twisted.logger import Logger
from twisted.internet import defer

from cheesepi.exceptions import NoSuchPeer

class CheeseRPCServerFactory(MsgpackServerFactory):
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

class CheeseRPCServer(MsgpackRPCServer):
    log = Logger()

    def _error(self, error):
        import traceback
        self.log.error("{error}\n{traceback}",
                       error=error, traceback=traceback.format_exc(error))
    def __init__(self, dao):
        self.dao = dao

    def _response(self, status, body):
        if status == True:
            return {'status':'success','result':body}
        else:
            return {'status':'failure','error':body}

    @defer.inlineCallbacks
    def remote_beacon(self, host, peer_id):
        """
        This remote method gets special handling in getRemoteMethod() in the
        CheeseRPCServerFactory class and thus receives the ip of the connecting
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
    def remote_register(self, host, peer_uuid):
        """
        This remote method gets special handling in getRemoteMethod() in the
        CheeseRPCServerFactory class and thus receives the ip of the connecting
        peer
        """
        from cheesepi.server.storage.models.entity import PeerEntity
        try:
            self.log.info("peer with uuid {peer_uuid} registering from host {host}",
                          peer_uuid=peer_uuid, host=host)
            entity = PeerEntity(host, peer_uuid)
            #result = yield self.dao.register_entity(peer_uuid, host, 'peer')
            result = yield self.dao.register_peer_entity(entity)
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
            import json
            # no valid task generation yet...
            tasks = yield self.dao.get_tasks(peer_id)
            task_str=json.dumps({'taskname':'ping',
                                 'landmark':'glindste.homeip.net',
                                 'time':4,
                                 'ping_count':3,
                                 'packet_size':32,
            })
            #for t in tasks:
                #task_str += str(t)
            self.log.info("got tasks {tasks}", tasks=task_str)
            defer.returnValue(self._response(True, task_str))
        except NoSuchPeer as e:
            defer.returnValue(self._response(False, "nosuchpeer"))
        except Exception as e:
            self._error(e)
            defer.returnValue(self._response(False, "error"))

    @defer.inlineCallbacks
    def remote_get_schedule(self, data):
        try:
            # TODO skeleton code right now...
            #self.log.info("Someone trying to get schedule for {}".format(data['uuid']))

            from cheesepi.server.scheduling.PingScheduler import PingScheduler
            ps = PingScheduler(data['uuid'])

            if 'method' in data:
                method = data['method']
            else: method = 'smart'

            if method == 'random':
                schedule = yield ps.get_random_schedule(data['num'])
            elif method == 'roundrobin':
                schedule = yield ps.get_round_robin_schedule(data['num'])
            elif method == 'smart':
                schedule = yield ps.get_schedule(data['num'])
            else:
                raise Exception("Unkown scheduling method {}".format(method))
            #self.log.info("got schedule: {schedule}", schedule=schedule)

            result = []
            for entity in schedule:
                result.append(entity.toDict())

            #from pprint import pformat
            #self.log.info("returning:\n{result}", result=pformat(result))

            defer.returnValue(self._response(True, result))
        except NoSuchPeer as e:
            self._error(e)
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
