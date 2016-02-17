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

import sys
import logging
import hashlib
import json

import cheesepi as cp
import dao

logger = cp.config.get_logger(__name__)

# Influx module, use legacy on RaspberryPi Linux
try:
	from influxdb.influxdb08 import InfluxDBClient
	from influxdb.influxdb08.client import InfluxDBClientError
except AttributeError as e:
	msg =  "Problem importing Python InfluxDB module!\n"
	msg += "Either due to this computer not having a timezone set.\n"
	msg += "Use `raspi-config` > Internationalisation Options to set one.\n"
	msg += "Alternatively, install 'pandas' through pip, rather than apt."
	print msg
	logger.error(msg)
	sys.exit(1)

host     = "localhost"
port     = 8086
username = "root"
password = "root"
database = "cheesepi"

class DAO_influx(dao.DAO):
	def __init__(self):
		#logging.info("Connecting to influx: %s %s %s" % (username,password,database))
		try: # Get a hold of a Influx connection
			self.conn = InfluxDBClient(host, port, username, password, database)
		except Exception as e:
			msg = "Error: Connection to Influx database failed! Ensure InfluxDB is running. "+str(e)
			logging.error(msg)
			print msg
			cp.config.make_databases()
			exit(1)

	def make_database(self, name):
		try:
			self.conn.create_database(name)
		except Exception as e:
			# database probably already exists
			pass

	def extract_series(self, dic):
		if len(dic)==1 and dic[0]['name']=='list_series_result':
			# mac version
			return [s[1] for s in dic[0]['points']]
		elif len(dic)>1 and dic[0]['points']==[]:
			# raspberry pi version
			return [s['name'] for s in dic]
		else:
			print "Error: parsing series list"


	def dump(self, since=-1):
		try:
			series_list = self.conn.query("list series")
			#series_list = self.conn.get_list_series()
		except Exception as e:
			msg = "Problem connecting to InfluxDB when listing series: "+str(e)
			print msg
			logging.error(msg)
			exit(1)
		series = self.extract_series(series_list)
		#print series
		# maybe prune series list?
		dumped_db = {}
		for series_name in series:
			#print series_name
			dumped_series = self.conn.query('select * from %s where time > %d ;' % (series_name,since*1000) )
			#print dumped_series
			dumped_db[series_name] = json.dumps(dumped_series)
		return dumped_db

	def format09(self,table,dic):
		#print [{"measurement":table,"fields":dic}]
		return [{'measurement':table,"database": "cheesepi","fields":dic,"tags": {"source":"dao"} }]
		#return json_body

	def format08(self, table, dic):
		for k in dic.keys():
				dic[k]=dic[k]
		#json_dic = [{"name":table, "columns":dic.keys(), "points":[dic.values()]}]
		json_str = '[{"name":"%s", "columns":%s, "points":[%s]}]' % (table,json.dumps(dic.keys()),json.dumps(dic.values()))
		#json_str = '[{"name":"ping", "columns":["test"], "points":["value"]}]'
		return json_str

	def slurp(self, op_type, points):
		"""Short cut to database write, useful for bulk writes"""
		#self.conn.write_points(op_type, points, batch_size=50)
		pass

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

		json = self.format08(op_type, dic)
		print "Saving %s Op: %s" % (op_type, json)
		try:
			return self.conn.write_points(json)
		except Exception as e:
			msg = "Database Influx "+op_type+" Op write failed! "+str(e)
			logging.error(msg)
			print msg
			#cp.config.make_databases()
			#exit(1)
			raise IOError(msg)
		return id

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
			json = self.format08("user", {attribute:value})
			return self.conn.write_points(json)
		except Exception as e:
			msg = "Problem connecting to InfluxDB: "+str(e)
			print msg
			logging.error(msg)
			exit(1)



