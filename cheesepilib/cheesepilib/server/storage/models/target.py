from __future__ import unicode_literals, absolute_import

import logging

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

	def get_hash(self):
		raise NotImplementedError("Abstract method 'get_hash' not implemented.")

	# TODO deprecated???
	def get_id(self):
		raise NotImplementedError("Abstract method 'get_id' not implemented.")

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

	def toDict(self):
		return {
			'type':'landmark',
			'ip':self._ip,
			'port':self._port,
			'domain':self._domain,
		}

	def get_id(self):
		return self._domain

	def get_hash(self):
		import hashlib
		hasher = hashlib.md5()
		hasher.update(self._domain)
		return hasher.hexdigest()


class PeerTarget(Target):

	log = logging.getLogger("cheesepi.server.storage.models.target.PeerTarget")

	@classmethod
	def fromDict(cls, dct):
		assert dct['type'] == 'peer'
		return PeerTarget(dct['ip'], dct['port'], dct['peer_id'])

	def __init__(self, ip, port, peer_id):
		self._ip = ip
		self._port = port
		self._peer_id = peer_id

	def toDict(self):
		return {
			'type':'peer',
			'ip':self._ip,
			'port':self._port,
			'peer_id':self._peer_id,
		}

	def get_hash(self):
		# peer_id should be a hash anyway
		return self._peer_id

	def get_id(self):
		return self._peer_id
