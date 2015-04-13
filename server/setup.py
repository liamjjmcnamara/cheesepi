#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect('localhost', 'urban', 'basketphone', 'sicspi')

with con:
	
	cur = con.cursor()

	#cur.execute("DROP TABLE IF EXISTS Ping")
        #cur.execute("DROP TABLE IF EXISTS User")
	#cur.execute("DROP TABLE IF EXISTS Operation")
	#cur.execute("DROP TABLE IF EXISTS Connection")
	#cur.execute("DROP TABLE IF EXISTS PI")
	#cur.execute("DROP TABLE IF EXISTS Central_DNS")

#=====================================================================
	#warnings off
	cur.execute("""SET sql_notes = 0""")
#=====================================================================

	cur.execute("""CREATE TABLE IF NOT EXISTS PI(
PID INT PRIMARY KEY AUTO_INCREMENT,
EthMAC varchar(20) UNIQUE
)""")


	cur.execute("""CREATE TABLE IF NOT EXISTS User(
PID INT,
mail varchar(40),
alias varchar(20) UNIQUE,
FOREIGN KEY (PID) REFERENCES PI(PID)
)""")

	cur.execute("""CREATE TABLE IF NOT EXISTS Connection(
CID INT PRIMARY KEY AUTO_INCREMENT, 
PID INT, 
MAC varchar(20),
FOREIGN KEY (PID) REFERENCES PI(PID),
UNIQUE KEY (PID, MAC)
)""")

	cur.execute("""CREATE TABLE IF NOT EXISTS Central_DNS(
Domain_ID INT PRIMARY KEY AUTO_INCREMENT,
Domain varchar(50),
IP varchar(20),
UNIQUE KEY (Domain, IP)
)""")

	cur.execute("""CREATE TABLE IF NOT EXISTS Operation(
OID BIGINT PRIMARY KEY AUTO_INCREMENT,
CID INT,
Tool ENUM('Ping', 'Traceroute') NOT NULL,
StartTime TIMESTAMP,
EndTime TIMESTAMP,
Status varchar(20),
FOREIGN KEY (CID) REFERENCES Connection(CID),
UNIQUE KEY (CID, StartTime, EndTime)
)""")

	#Make sure all the tools are available!
	cur.execute("""ALTER TABLE Operation CHANGE Tool Tool ENUM('Ping', 'Traceroute', 'Httping')""")

	cur.execute("""CREATE TABLE IF NOT EXISTS Ping(
PID INT,
OID BIGINT,
SA varchar(20),
Domain_ID INT,
minRTT FLOAT,
avgRTT FLOAT,
maxRTT FLOAT,
ival INT,
size INT,
packet_loss varchar(50),
file_path varchar(50),
FOREIGN KEY (PID) REFERENCES PI(PID),
FOREIGN KEY (OID) REFERENCES Operation(OID),
FOREIGN KEY (Domain_ID) REFERENCES Central_DNS(Domain_ID),
UNIQUE KEY (OID)
)""")

	cur.execute("""CREATE TABLE IF NOT EXISTS Traceroute(
PID INT,
OID BIGINT,
SA varchar(20),
Domain_ID INT,
size INT,
file_path varchar(50),
FOREIGN KEY (PID) REFERENCES PI(PID),
FOREIGN KEY (OID) REFERENCES Operation(OID),
FOREIGN KEY (Domain_ID) REFERENCES Central_DNS(Domain_ID),
UNIQUE KEY (OID)
)""")

	cur.execute("""CREATE TABLE IF NOT EXISTS Hops(
OID BIGINT,
Hop_number INT,
Packet_number INT,
Domain_ID INT,
RTT FLOAT,
FOREIGN KEY (OID) REFERENCES Operation(OID),
FOREIGN KEY (Domain_ID) REFERENCES Central_DNS(Domain_ID),
UNIQUE KEY (OID, Hop_number, Packet_number)
)""")

	#pretty much a straight up copy of the Ping table
	cur.execute("""CREATE TABLE IF NOT EXISTS Httping(
PID INT,
OID BIGINT,
SA varchar(20),
Domain_ID INT,
minRTT FLOAT,
avgRTT FLOAT,
maxRTT FLOAT,
ival INT,
size INT,
packet_loss varchar(50),
file_path varchar(50),
FOREIGN KEY (PID) REFERENCES PI(PID),
FOREIGN KEY (OID) REFERENCES Operation(OID),
FOREIGN KEY (Domain_ID) REFERENCES Central_DNS(Domain_ID),
UNIQUE KEY (OID)
)""")
#===================================================================
	#warnings back on
	cur.execute("""SET sql_notes = 1""")
#===================================================================
##ADD SOME DATA : D
'''
	cur.execute("""INSERT INTO PI VALUES 
(NULL, 'abc'), 
(NULL, 'def')
""")

	cur.execute("""INSERT INTO User VALUES
(1, 'guy@site.com', 'PIrate'),
(2, 'person@web.se', 'PIkachu')
""")

	cur.execute("""INSERT INTO Connection VALUES 
(NULL, 1, 'abc'), 
(NULL, 2, 'def'), 
(NULL, 2, 'ghi')
""")

	cur.execute("""INSERT INTO Central_DNS VALUES 
(NULL, 'www.bbc.com', '1.2.3.4'), 
(NULL, 'www.bbc.com', '1.2.3.5'), 
(NULL, 'www.sics.se', '6.7.8.9')
""")

	cur.execute("""INSERT INTO Operation VALUES
(NULL, 1, 'Ping', NOW(), NOW(), '0'),
(NULL, 1, 'Ping', NOW(), NOW(), '1'),
(NULL, 2, 'Ping', NOW(), NOW(), '0'),
(NULL, 2, 'Traceroute', NOW(), NOW(), '4')
""")

	cur.execute("""INSERT INTO Ping VALUES
(1, 1, "193.10.66.2", 1, 25.0, 30.0, 35.0, 10, 64, "0%", "path"),
(1, 2, "193.10.66.2", 1, 24.0, 32.0, 37.0, 10, 64, "10%", "path2"),
(1, 1, "193.10.66.4", 2, 10.0, 12.0, 14.0, 10, 64, "0%", "path3")
""")
'''

con.commit()
con.close()

