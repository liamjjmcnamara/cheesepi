#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import MySQLdb as mdb
from influxdb import InfluxDBClient

db_host      = "localhost"
db_username  = "root"
db_password  = ""
db_db        = "Measurement"
curMain      = None
connectioNDB = None


def main():
	columns =['ts','src','domain','domain_ip','start_time','end_time','minrtt','avgrtt','maxrtt','packet_loss','eth_mac','curr_mac','packet_size','number_pings']
	connectionPI = mdb.connect(db_host, db_username, db_password, db_db)
	client = InfluxDBClient('localhost', 8086, 'root', 'root', 'measurements')
	#client.create_database('ping')

	with connectionPI:
		curPI = connectionPI.cursor()
		query = """SELECT * FROM ping"""
		curPI.execute(query)
		rows = curPI.fetchall()

		for row in rows:
			#parse(row)
			save_influx(client, columns, row)

	connectionPI.commit()
	connectionPI.close()

def make_serialisable(columns,values):
	number_columns =['minrtt','avgrtt','maxrtt','packet_loss','packet_size','number_pings']
	#columns =['ts','src','domain','domain_ip','start_time','end_time','minrtt','avgrtt','maxrtt','packet_loss','eth_mac','curr_mac','packet_size','number_pings']
	a=[]
	for i in xrange(len(columns)):
		if type(values[i]) is datetime.datetime:
			a.append(int(values[i].strftime("%s")))
		elif columns[i]=="packet_loss":
			a.append(float(values[i][:-1]))
		elif columns[i] in number_columns:
			a.append(float(values[i]))
		else:
			a.append(values[i])
	return a

def save_influx(client, columns, values):
	json = [{
    "name": "ping",
    "points": [make_serialisable(columns,values) ],
    "columns": columns
	}]
	print json
	client.write_points(json)


if __name__ == "__main__":
    main()
