from __future__ import unicode_literals, absolute_import

import logging
import uuid

from cheesepilib.exceptions import UnsupportedTargetType

class Target(object):

	log = logging.getLogger("cheesepi.server.storage.models.target.Target")

	@classmethod
	def fromDict(cls, dct):
		from pprint import pformat
		target_type = dct['type']

		if target_type == 'landmark': return LandmarkTarget.fromDict(dct)
		if target_type == 'peer': return PeerTarget.fromDict(dct)
		else: raise UnsupportedTargetType("Unknown target type '{}'.".format(target_type))

	def toDict(self):
		raise NotImplementedError("Abstract method 'toDict' not implemented.")

	def get_uuid(self):
		raise NotImplementedError("Abstract method 'get_uuid' not implemented.")

class LandmarkTarget(Target):

	log = logging.getLogger("cheesepi.server.storage.models.target.LandmarkTarget")

	@classmethod
	def fromDict(cls, dct):
		assert dct['type'] == 'landmark'
		return LandmarkTarget(dct['ip'], dct['port'], dct['domain'])

	def __init__(self, ip, port, domain):
		self._ip = ip
		self._port = port
		self._domain = domain
		self._uuid = uuid.uuid5(uuid.NAMESPACE_DNS, domain)

	def toDict(self):
		return {
			'type':'landmark',
			'ip':self._ip,
			'port':self._port,
			'domain':self._domain,
			'uuid':str(self._uuid),
		}

	def get_uuid(self):
		return str(self._uuid)


class PeerTarget(Target):

	log = logging.getLogger("cheesepi.server.storage.models.target.PeerTarget")

	@classmethod
	def fromDict(cls, dct):
		assert dct['type'] == 'peer'
		return PeerTarget(dct['ip'], dct['port'], dct['uuid'])

	def __init__(self, ip, port, peer_uuid):
		self._ip = ip
		self._port = port
		self._uuid = uuid.UUID(peer_uuid)
		assert peer_uuid == str(self._uuid)

	def toDict(self):
		return {
			'type':'peer',
			'ip':self._ip,
			'port':self._port,
			'uuid':str(self._uuid),
		}

	def get_uuid(self):
		return str(self._uuid)
