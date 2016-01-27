#!/usr/bin/python

import os
import datetime
import MySQLdb as mdb


def main():
	connectionDB = mdb.connect("localhost", "urban", "basketphone", "sicspi")
	cur = connectionDB.cursor()
        listOfPIs = pi_List(connectionDB, cur)
        pis_Not_Send_Data(listOfPIs,connectionDB, cur)
	connectionDB.close()
#A method that list out pis who do not send data today
def pis_Not_Send_Data(listOfPIs,connectionDB, cur):
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d")
        now = datetime.datetime.strptime(now, "%Y-%m-%d")
        #The list Pis which do not send data will be save in a file
        myfile = open("ListPIs.txt",'a+')
        myfile.write("\nPis which do not send data today: " + str(now))
        pisNotSendData = []
	print "Start looking for Pis who do not send data"
        #Iterating on the registered Pis
        for pi in listOfPIs:
                #Retrieves the starting time of the last data send by the PI  
		selectQuery = """SELECT StartTime FROM Operation,Ping,PI 
				 WHERE Operation.OID = Ping.OID AND Ping.PID = PI.PID AND 
                                 PI.EthMAC = '%s' ORDER BY Operation.StartTime DESC LIMIT 1;"""%str(pi[0])
                cur.execute(selectQuery)
		startTime = cur.fetchall()
		connectionDB.commit()
		startTime = startTime[0][0].strftime("%Y-%m-%d")
		startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d")
		difference = now - startTime
		print difference
		#If the starting time is not today
		if (difference.days > 0):
			pisNotSendData.append(str(pi[0])) 
        if pisNotSendData:
		for pi in pisNotSendData:
                        myfile.write("\n" + str(pi))
        myfile.close()
	print "Writes the list of Pis who do not send data in the file"

#A metho that returns list of registerd pis in the central server
def pi_List(connectionDB, cur):
        selectQuery = """SELECT EthMAC from PI"""
        cur.execute(selectQuery)
        rows = cur.fetchall()
        connectionDB.commit()
        #connectionDB.close()
        return rows


if __name__ == "__main__":
    main()

