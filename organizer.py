#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import datetime

connectionDB = None
curMain = None

def main():
	global connectionDB
	global curMain

	connectionPI = mdb.connect('localhost', 'urban', 'basketphone', 'buffer')

	connectionDB = mdb.connect("localhost", "urban", "basketphone", "sicspi")

	with connectionPI:
		curPI = connectionPI.cursor()
		query = """SELECT distinct(EthernetMacAddress) from ping"""
		curPI.execute(query)
		macs = curPI.fetchall()


	with connectionDB:
		curMain = connectionDB.cursor()
		for mac in macs:
			print "Handling: ", mac[0]
			query = """ SELECT max(startTime) FROM Operation, Ping, PI where Operation.OID=Ping.OID AND Ping.PID=PI.PID and PI.EthMAC='%s'"""%mac[0]
			curMain.execute(query)
			result = curMain.fetchall()
			modifier = ""
			if result[0][0]:
				result =  result[0][0].strftime("""%Y-%m-%d %H:%M:%S""")
				query = """SELECT * FROM ping WHERE StartingTime > '%s' and ping.EthernetMacAddress = '%s' ORDER BY StartingTime""" %(result, mac[0])
			else:
				query = """SELECT * FROM ping WHERE ping.EthernetMacAddress = '%s' ORDER BY StartingTime""" %mac[0]
			
			with connectionPI:
				curPI = connectionPI.cursor()
				curPI.execute(query)
				rows = curPI.fetchall()
				
				for row in rows:
					parse(row)

	connectionDB.close()
		
	connectionPI.commit()
	connectionPI.close()

def parse(row):
	global connectionDB
	global curMain
	ts = row[0]
	src = str(row[1])
	domain = str(row[2])
	domain_ip = str(row[3])
	start_time = row[4]
	end_time = row[5]
	minrtt = float(row[6])
	avgrtt = float(row[7])
	maxrtt = float(row[8])
	packet_loss = str(row[9])
	eth_mac = str(row[10])
	curr_mac = str(row[11])
	packet_size = int(row[12])
	number_pings = int(row[13])

#(datetime.datetime(2015, 3, 16, 11, 36, 18), '193.10.66.2', 'bbc.com', '212.58.246.104', #datetime.datetime(2015, 3, 16, 10, 36, 9), datetime.datetime(2015, 3, 16, 10, 36, 9), 36.146, #36.209, 36.301, '0%', 'b8:27:eb:16:7d:a6', 'b8:27:eb:16:7d:a6', 64L, 10L)

	
	with connectionDB:
		
		PID = addPI(eth_mac)
		connectionDB.commit()
		CID = addConnection(PID, curr_mac)
		connectionDB.commit()
		Domain_ID = addDomain(domain, domain_ip)
		connectionDB.commit()

		OID = addOperation(CID, "Ping", start_time, end_time, "0")
		addPing(PID, OID, src, Domain_ID, minrtt, avgrtt, maxrtt, number_pings, packet_size, packet_loss, "file_path_here")
		connectionDB.commit()

	connectionDB.commit()

def addPI(eth_mac):
	global curMain
	global connectionDB
	
	with connectionDB:
		query = """SELECT PID from PI where PI.EthMAC='%s'"""%eth_mac
		curMain.execute(query)
		result = curMain.fetchall()
		if not result:
			query = """INSERT INTO PI VALUES(NULL, '%s')"""%eth_mac
			curMain.execute(query)
			query = """SELECT LAST_INSERT_ID()"""
			curMain.execute(query)
			result = curMain.fetchall()
		return result[0][0]

def addConnection(PID, curr_mac):
	global curMain
	global connectionDB

	with connectionDB:
		query = """SELECT CID FROM Connection WHERE Connection.PID=%s AND Connection.MAC='%s'"""%(PID, curr_mac)
		curMain.execute(query)
		result = curMain.fetchall()
		if not result:
			query = """INSERT INTO Connection VALUES(NULL, %s, '%s')"""%(PID, curr_mac)
			curMain.execute(query)
			query = """SELECT LAST_INSERT_ID()"""
			curMain.execute(query)
			result = curMain.fetchall()
		return result[0][0]

def addOperation(CID, Tool, start_time, end_time, status):
	global curMain
	global connectionDB

	with connectionDB:
		query = """INSERT INTO Operation VALUES(NULL, %s, '%s', '%s', '%s', '%s')"""%(CID, Tool, start_time, end_time, status)
		curMain.execute(query)
		query = """SELECT LAST_INSERT_ID()"""
		curMain.execute(query)
		result = curMain.fetchall()

		return result[0][0]

def addDomain(domain, domain_ip):
	global curMain
	global connectionDB

	with connectionDB:
		query = """SELECT Domain_ID FROM Central_DNS WHERE Central_DNS.Domain='%s' AND Central_DNS.IP='%s'"""%(domain, domain_ip)
		curMain.execute(query)
		result = curMain.fetchall()
		if not result:
			query = """INSERT INTO Central_DNS VALUES(NULL, '%s', '%s')"""%(domain, domain_ip)
			curMain.execute(query)
			query = """SELECT LAST_INSERT_ID()"""
			curMain.execute(query)
			result = curMain.fetchall()


		return result[0][0]

def addPing(PID, OID, src, Domain_ID, minrtt, avgrtt, maxrtt, number_pings, packet_size, packet_loss, status):
	global curMain
	global connectionDB

	with connectionDB:
		query = """INSERT INTO Ping VALUES(%s, %s, '%s', %s, %s, %s, %s, %s, %s, '%s', '%s')"""%(PID, OID, src, Domain_ID, minrtt, avgrtt, maxrtt, number_pings, packet_size, packet_loss, status)
		curMain.execute(query)

if __name__ == "__main__":
    main()
