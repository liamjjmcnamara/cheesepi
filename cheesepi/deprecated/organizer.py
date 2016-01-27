#!/usr/bin/python
# -*- coding: utf-8 -*-import MySQLdb as mdb

import MySQLdb as mdb
import datetime

def main():

	connectionDB = mdb.connect("localhost", "urban", "basketphone", "sicspi")
	
	with connectionDB:
		cur = connectionDB.cursor()
		
		query = """insert ignore into PI (EthMAC) select distinct(EthernetMacAddress) from buffer.ping"""
		cur.execute(query)

		query = """insert ignore into Connection (PID, MAC) select distinct(PI.PID), buffer.ping.currentMacAddress from PI, buffer.ping where PI.EthMAC = buffer.ping.ethernetMacAddress group by PI.PID"""
		cur.execute(query)

		query = """insert ignore into Central_DNS(IP, Domain) select distinct(bp.destinationAddress), bp.destinationDomain from buffer.ping as bp"""
		cur.execute(query)

		query = """insert ignore into Operation (CID, Tool, StartTime, EndTime, Status) select CID, "Ping", bp.StartingTime, bp.EndingTime, "0" from Connection, PI, buffer.ping as bp where PI.EthMAC=bp.EthernetMacAddress and bp.currentMacAddress=Connection.MAC and Connection.PID = PI.PID"""
		cur.execute(query)

		query = """insert ignore into Ping (PID, OID, SA, Domain_ID, minRTT, avgRTT, maxRTT, ival, size, packet_loss, file_path) select PI.PID, OID, bp.sourceAddress, Central_DNS.Domain_ID, bp.minimumRTT, bp.averageRTT, bp.maximumRTT, bp.numberOfPings, bp.packetSize, bp.packetloss, "" from buffer.ping as bp, PI, Connection, Central_DNS, Operation where PI.EthMAC=bp.EthernetMacAddress and bp.currentMacAddress=Connection.MAC and Connection.PID = PI.PID and Central_DNS.Domain = bp.destinationDomain and Central_DNS.IP=bp.destinationAddress and Operation.CID = Connection.CID and Operation.StartTime=bp.StartingTime and Operation.EndTime=bp.EndingTime"""
		cur.execute(query)

	connectionDB.commit()
	connectionDB.close()

	#Purge the buffer
	connectionBuffer = mdb.connect("localhost", "urban", "basketphone", "buffer")
	with connectionBuffer:
		cur = connectionBuffer.cursor()

		query = """delete from ping"""
		cur.execute(query)
	
	connectionBuffer.commit()
	connectionBuffer.close()


if __name__ == "__main__":
    main()
