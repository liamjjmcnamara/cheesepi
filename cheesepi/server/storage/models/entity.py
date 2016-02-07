from __future__ import unicode_literals, absolute_import

import logging
import uuid

from cheesepi.exceptions import UnsupportedEntityType

class Entity(object):

	log = logging.getLogger("cheesepi.server.storage.models.entity.Entity")

	@classmethod
	def fromDict(cls, dct):
		from pprint import pformat
		entity_type = dct['type']

		if entity_type == 'landmark': return LandmarkEntity.fromDict(dct)
		if entity_type == 'peer': return PeerEntity.fromDict(dct)
		else: raise UnsupportedEntityType("Unknown entity type '{}'.".format(entity_type))

	def toDict(self):
		raise NotImplementedError("Abstract method 'toDict' not implemented.")

	def get_uuid(self):
		raise NotImplementedError("Abstract method 'get_uuid' not implemented.")

class LandmarkEntity(Entity):

	log = logging.getLogger("cheesepi.server.storage.models.entity.LandmarkEntity")

	@classmethod
	def fromDict(cls, dct):
		assert dct['type'] == 'landmark'
		return LandmarkEntity(dct['ip'], dct['domain'])

	def __init__(self, ip, domain):
		self._ip = ip
		#self._port = port
		self._domain = domain
		self._uuid = uuid.uuid5(uuid.NAMESPACE_DNS, domain)

	def toDict(self):
		return {
			'type':'landmark',
			'ip':self._ip,
			'domain':self._domain,
			'uuid':str(self._uuid),
		}

	def get_uuid(self):
		return str(self._uuid)


class PeerEntity(Entity):

	log = logging.getLogger("cheesepi.server.storage.models.entity.PeerEntity")

	@classmethod
	def fromDict(cls, dct):
		assert dct['type'] == 'peer'
		return PeerEntity(dct['ip'], dct['uuid'])

	def __init__(self, ip, peer_uuid):
		self._ip = ip
		#self._port = port
		self._uuid = uuid.UUID(peer_uuid)
		assert peer_uuid == str(self._uuid)

	def toDict(self):
		return {
			'type':'peer',
			'ip':self._ip,
			'uuid':str(self._uuid),
		}

	def get_uuid(self):
		return str(self._uuid)
