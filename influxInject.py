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

def make_serialisable(values):
	a=[]
	for v in values:
		if type(v) is datetime.datetime:
			a.append(v.strftime("%s"))
		else:
			a.append(v)
	return a

def save_influx(client, columns, values):
	json = [{
    "points": [make_serialisable(values) ],
    "name": "ping",
    "columns": columns
	}]
	print json
	client.write_points(json)


if __name__ == "__main__":
    main()
