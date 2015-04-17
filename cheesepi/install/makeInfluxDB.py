#!/usr/bin/env python

# Influx
from influxdb import InfluxDBClient
# legacy module
#from influxdb.influxdb08 import InfluxDBClient

host	 = "localhost"
port	 = 8086
username = "root"
password = "root"
database = "cheesepi"

conn = InfluxDBClient(host, port, username, password, database)
conn.create_database(database)
conn.create_database("grafana")

