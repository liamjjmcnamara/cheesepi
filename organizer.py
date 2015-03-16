#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

connectioNDB = None
curMain = None

def main():
	connectionPI = mdb.connect('localhost', 'urban', 'basketphone', 'buffer')

	with connectionPI:
	
		curPI = connectionPI.cursor()
		query = """SELECT * FROM ping"""
		curPI.execute(query)
		rows = curPI.fetchall()

		for row in rows:
			parse(row)
		
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

	connectionDB = mdb.connect("localhost", "urban", "basketphone", "sicspi")
	
	with connectionDB:
		curMain = connectionDB.cursor()
		
		PID = addPI(eth_mac)
		CID = addConnection(PID, curr_mac)
		OID = addOperation(CID, "Ping", start_time, end_time, "0")
		Domain_ID = addDomain(domain, domain_ip)
		print Domain_ID
		#addPing(PID, OID, src, Domain_ID, minrtt, avgrtt, maxrtt, number_pings, packet_size, packet_loss, "mjau")

	connectionDB.commit()
	connectionDB.close()

def addPI(eth_mac):
	global curMain
	global connectionDB
	
	with connectionDB:
		query = """SELECT PID from PI where PI.EthMAC='%s'"""%eth_mac
		curMain.execute(query)
		result = curMain.fetchall()
#		print "PI", result
		if not result:
#			print "getting id"
			query = """INSERT INTO PI VALUES(NULL, '%s')"""%eth_mac
			curMain.execute(query)
			query = """SELECT @last := LAST_INSERT_ID()"""
			curMain.execute(query)
			result = curMain.fetchall()
#			print result
		connectionDB.commit()
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
			query = """SELECT @last := LAST_INSERT_ID()"""
			curMain.execute(query)
			result = curMain.fetchall()
		connectionDB.commit()	
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
			query = """SELECT @last := LAST_INSERT_ID()"""
			curMain.execute(query)
			result = curMain.fetchall()
		connectionDB.commit()		


		return result[0][0]
if __name__ == "__main__":
    main()
