#!/usr/bin/env python 

import MySQLdb


db = MySQLdb.connect("localhost", "measurement", "MP4MDb", "Measurement")
curs=db.cursor()
curs.execute ("SELECT * FROM ping")

print "\TimeStamp     	          SA                  DA                    MinRTT    AvgRTT   MaxRTT    Packet Loss"
print "==============================================================================================================="

for row in curs.fetchall():
    print str(row[0]) +"  "+str(row[1])+"  "+\
                str(row[2]) +"       " +str(row[3])+ "   "+\
		str(row[4]) +"  " +str(row[5]) +"    "+ str(row[6])

db.commit()
db.close()  
