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
"""

import logging
import hashlib
import json
import traceback

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from requests.exceptions import ConnectionError

import cheesepilib as cp
import dao

host     = "localhost"
port     = 8086
username = "root"
password = "root"
database = "cheesepi"

class DAO_influx09(dao.DAO):
	def __init__(self):
		logging.info("Connecting to influx: %s %s %s" % (username,password,database))
		try: # Get a hold of a Influx connection
			self.conn = InfluxDBClient(host, port, username, password, database)
		except Exception as e:
			msg = "Error: Connection to Influx database failed! Ensure InfluxDB is running. "+str(e)
			logging.error(msg)
			print msg
			cp.config.make_databases()
			exit(1)


	def dump(self, since=-1):
		try:
			series = self.conn.get_list_series()
		except Exception as e:
			msg = "Problem connecting to InfluxDB when listing series: "+str(e)
			print msg
			logging.error(msg)
			exit(1)

		# maybe prune series?
		dumped_db = {}
		for s in series:
			series_name = s['name']
			print series_name
			dumped_series = self.conn.query('select * from %s where time > %d limit 5;' % (series_name,0*1000) )
			print dumped_series.raw['results']
			dumped_db[series_name] = json.dumps(dumped_series.raw['results'])
		return dumped_db



	def toFormat(self,table,dic):
		#print [{"measurement":table,"fields":dic}]
		return [{'measurement':table,"database": "cheesepi","fields":dic,"tags": {"source":"dao"} }]
		#return json_body

	# Operator interactions
	def write_op(self, op_type, dic, binary=None):
		if not self.validate_op(op_type):
			logging.warning("Operation of type %s not valid: " % (op_type, str(dic)))
			return
		#if binary!=None:
		#	 # save binary, check its not too big
		#	 dic['binary'] = bson.Binary(binary)
		config = cp.config.get_config()
		dic['version'] = config['version']
		md5 = hashlib.md5(config['secret']+str(dic)).hexdigest()
		dic['sign']    = md5

		points=self.toFormat(op_type,dic)
		print "Saving %s Op: %s" % (op_type, str(points))
		try:
			result = self.conn.write_points(points)
		except InfluxDBClientError as e:
			if e.code==204: # success!
				return True
			traceback.print_exc()
		except ConnectionError as e:
			print "Database connection error, is the database server running?"
			return None
		except Exception as e:
			msg = "Database Influx "+op_type+" Op write failed! "+str(e)
			print type(e)
			print msg
			logging.error(msg)
			#cheesepi.config.make_databases()
			#exit(1)
			return None
		return result

	def read_op(self, op_type, timestamp=0, limit=100):
		op = self.conn.query('select * from '+op_type+' limit 1;')
		return op



	## User level interactions
	# Note that assignments are not deleted, but the most recent assignemtn
	# is always returned
	def read_user_attribute(self, attribute):
		try:
			result = self.conn.query('select %s from user limit 1;' % attribute)
			if result==[]:
				return -1
			column_index = result[0]['columns'].index(attribute)
			value = result[0]['points'][0][column_index]
		except InfluxDBClientError:
			#msg = "Problem connecting to InfluxDB: "+str(e)
			#print msg
			#logging.error(msg)
			return -1
		except Exception as e:
			msg = "Problem connecting to InfluxDB: "+str(e)
			print msg
			exit(1)
		return value

	def write_user_attribute(self, attribute, value):
		# check we dont already exist
		try:
			print "Saving user attribute: %s to %s " % (attribute, value)
			#json = self.to_json("user", {attribute:value})
			json = self.toFormat("user", {attribute:value})
			print json
			return self.conn.write_points(json)
		except Exception as e:
			msg = "Problem connecting to InfluxDB: "+str(e)
			print msg
			logging.error(msg)
			exit(1)


	def to_json(self, table, dic):
		for k in dic.keys():
				dic[k]=dic[k]
		#json_dic = [{"name":table, "columns":dic.keys(), "points":[dic.values()]}]
		#json_str = '[{"name":"%s", "columns":%s, "points":[%s]}]' % (table,json.dumps(dic.keys()),json.dumps(dic.values()))

		json_str = '[{"measurement":"%s", "fields":%s, ' % (table,"")
		#json_str = '[{"name":"ping", "columns":["test"], "points":["value"]}]'
		return json_str


