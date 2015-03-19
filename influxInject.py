#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import sys
import time

import MySQLdb as mdb
from influxdb import InfluxDBClient

db_host      = "localhost"
db_username  = "root"
db_password  = "MP4MDb"
db_db        = "Measurement"
curMain      = None
connectioNDB = None


def main():
	#columns =['ts','src','domain','domain_ip','start_time','end_time','minrtt','avgrtt','maxrtt','packet_loss','eth_mac','curr_mac','packet_size','number_pings']
	columns =['ts','src','domain','domain_ip','start_time','end_time','minrtt','avgrtt','maxrtt','packet_loss','eth_mac',"curr_mac",'packet_size','number_pings']
	connectionPI = mdb.connect(db_host, db_username, db_password, db_db)
	client = InfluxDBClient('localhost', 8086, 'root', 'root', 'measurements')
	#client.create_database('ping')
	from_time = get_last_update(client)

	with connectionPI:
		curPI = connectionPI.cursor()
		query = "SELECT * FROM ping WHERE UNIX_TIMESTAMP(ts) > "+str(from_time)
		print query
		curPI.execute(query)
		rows = curPI.fetchall()

		for row in rows:
			#parse(row)
			save_influx(client, columns, row)

	connectionPI.commit()
	connectionPI.close()

def get_last_update(client):
	result = client.query('select ts from ping limit 1;')
	from_time = result[0]['points'][0][2]
	return from_time

def make_serialisable(columns,values):
	number_columns =['minrtt','avgrtt','maxrtt','packet_loss','packet_size','number_pings']
	#columns =['ts','src','domain','domain_ip','start_time','end_time','minrtt','avgrtt','maxrtt','packet_loss','eth_mac','curr_mac','packet_size','number_pings']
	a=[int(values[4].strftime("%s"))]
	for i in xrange(len(columns)):
		print i,columns[i],values[i]
		try:
			if columns[i]=="time":
				a.append(int(values[4].strftime("%s")))
			elif type(values[i]) is datetime.datetime:
				a.append(int(values[i].strftime("%s")))
			elif columns[i]=="packet_loss":
				a.append(float(values[i][:-1]))
			elif columns[i] in number_columns:
				a.append(float(values[i]))
			else:
				a.append(values[i])
		except Exception as e:
			print "warning, value problem",e
	print a
	return a

def save_influx(client, columns, values):
	exportcolumns=columns[:]
	exportcolumns.insert(0,"time")
	json = [{
    "name": "ping",
    "points": [make_serialisable(columns,values) ],
    "columns": exportcolumns
	}]
	print json
	try:
		client.write_points(json)
	except Exception as e:
		print "Influx was unhappy: ",e


if __name__ == "__main__":
	while (True):
		main()
		time.sleep(300)
