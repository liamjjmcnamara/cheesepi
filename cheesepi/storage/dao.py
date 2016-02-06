""" Copyright (c) 2015, Swedish Institute of Computer Science
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
	  * Redistributions of source code must retain the above copyright
		notice, this list of conditions and the following disclaimer.
	  * Redistributions in binary form must reproduce the above copyright
		notice, this list of conditions and the following disclaimer in the
		documentation and/or other materials provided with the distribution.
	  * Neither the name of The Swedish Institute of Computer Science nor the
		names of its contributors may be used to endorse or promote products
		derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE SWEDISH INSTITUTE OF COMPUTER SCIENCE BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Authors: ljjm@sics.se
Testers:
Description: Abstract class to be subclassed by specific database storage engine
"""

import logging

class DAO:
	def __init__(self):
		pass

	def close(self):
		pass

	def make_database(self, name):
		pass

	def dump(self, since=None):
		msg ="Method not implemented in DAO class"
		logging.error(msg)
		return msg

	def slurp(self):
		"""Ingest many data points at once"""
		logging.error("Method not implemented in this DAO class")
		pass

	# Operator interactions
	def write_op(self, op_type, dic, binary=None):
		logging.error("Method not implemented in this DAO class")
		pass

	def read_op(self, op_type, timestamp=0, limit=100):
		logging.error("Method not implemented in this DAO class")
		return None

	# user level interactions
	def write_user_attribute(self, attribute, value):
		pass

	def read_user_attribute(self, attribute):
		logging.error("Method not implemented in this DAO class")
		return None

	# misversion formatting!
	def to_json(self, table, dic):
		for k in dic.keys():
			dic[k]=dic[k]
		json_str = '[{"measurement":"%s", "fields":%s} "database":"cheesepi"]' % (table,dic)
		return json_str

# The following need not be reimplemented in subclasses

	def validate_op(self, op_type):
		# should check the op is structured correctly
		return True


