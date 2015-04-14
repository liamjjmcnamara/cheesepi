#!/usr/bin/python
import MySQLdb
import warnings
import socket
import fcntl
import struct
def main():
	ethmac = getEthMAC()
	prefix = ethmac + "-"
	db = MySQLdb.connect("localhost", "measurement", "MP4MDb", "Measurement")
	curs=db.cursor()
	#The auto increment id from the table is going to be concatenated the main id in traceroute table
	#For example 04:7d:7b:36:99:79-001 to uniqly identify a traceroute
	traceroute_seq = """CREATE TABLE if not exists Traceroute_seq(
				id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY);"""
	traceroute = """CREATE TABLE if not exists Traceroute(
				ID VARCHAR(100) NOT NULL PRIMARY KEY, 
				ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
				ethernetMacAddress TEXT, currentMacAddress TEXT, sourceAddress TEXT, 
				destinationDomain TEXT, destinationAddress TEXT, 
				startingTime DATETIME, endingTime DATETIME);"""
	hop = """CREATE TABLE if not exists Hop( 
				ID VARCHAR(100) NOT NULL, hopNumber INTEGER, packetNumber INTEGER,
				packetDomainAddress TEXT, packetDestinationAddress TEXT, RTT FLOAT,
				FOREIGN KEY (ID) REFERENCES Traceroute(ID) ON DELETE CASCADE);"""
	#This trigger is used to 
	createTrigger = """CREATE TRIGGER Trg_Traceroute_insert BEFORE INSERT ON Traceroute
			   FOR EACH ROW BEGIN
  				INSERT INTO Traceroute_seq VALUES (NULL);
  				SET NEW.ID = CONCAT('%s', LPAD(LAST_INSERT_ID(), length(LAST_INSERT_ID()), '0'));
			   END;""" %prefix
	#insertToTable = """INSERT INTO table1 (name) 
          #                             VALUES ('Biniam'), ('Urban');"""
	with warnings.catch_warnings():
                warnings.simplefilter("ignore")
		curs.execute(traceroute_seq)
		curs.execute(traceroute)
		curs.execute(hop)
		curs.execute(createTrigger)
		#curs.execute(insertToTable)
	db.commit()
	db.close()

#get the ethernet mac address of this device
def getEthMAC(ifname = "eth0"):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]


if __name__ == "__main__":
 main()
