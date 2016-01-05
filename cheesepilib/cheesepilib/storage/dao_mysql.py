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

# PyMongo
import MySQLdb

import dao

class DAO_mysql(dao.DAO):
	def __init__(self):
		try: # Get a hold of a MySQL connection
			self.conn = MySQLdb.connect("localhost", "measurement", "MP4MDb", "Measurement")
		except:
			msg = "Error: Connection to MySQL database failed! Ensure MySQL is running."
			logging.error(msg)
			print msg
			exit(1)

		if not self.conn:
			logging.error("MySQL database connnection failed")
			exit(1)

		#disable warnings
		cursor = self.conn.cursor()
		cursor.execute("""SET sql_notes = 0""")

		pingquery = """CREATE TABLE IF NOT EXISTS ping(ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			sourceAddress TEXT, destinationDomain TEXT, destinationAddress TEXT,
			startingTime DATETIME, endingTime DATETIME, minimumRTT FLOAT,
			averageRTT FLOAT, maximumRTT FLOAT, packetLoss TEXT,
			ethernetMacAddress TEXT, currentMacAddress TEXT, packetSize INTEGER,
			numberOfPings INTEGER);"""
		cursor.execute(pingquery)

		httpquery = """CREATE TABLE IF NOT EXISTS httping(ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			sourceAddress TEXT, destinationDomain TEXT, destinationAddress TEXT,
			startingTime DATETIME, endingTime DATETIME, minimumRTT FLOAT,
			averageRTT FLOAT, maximumRTT FLOAT, packetLoss TEXT,
			ethernetMacAddress TEXT, currentMacAddress TEXT, packetSize INTEGER,
			numberOfHttpings INTEGER);"""
		cursor.execute(httpquery)

		#enable warnings
		cursor.execute("""SET sql_notes = 1""")

	def close(self):
		self.conn.close()


	# operator level interactions
	def write_op(self, op_type, dic, binary=None):
		names = ""
		values = ""
		for key, value in dic.iteritems():
			names = names + key + ", "
			values = values + str(value) + ", "

		names = names[:-2]
		values = values[:-2]

		query = """INSERT INTO %s (%s) VALUES (%s)""" % (op_type, names, values)
		with self.conn:
			cursor = self.conn.cursor();
			cursor.execute(query)
			self.conn.commit()


	def read_op(self, op_type, timestamp=0, limit=100):
	#check last push and grab the rest?
		pass


	# user level interactions
	def read_user_attribute(self):
		pass


	def write_user_attribute(self, attribute, value):
		pass

