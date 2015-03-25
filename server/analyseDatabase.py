#!/usr/bin/python

import os
import datetime
import MySQLdb as mdb


def main():
        listOfPIs = pi_List()
        pis_Not_Send_Data(listOfPIs)

#A method that list out pis who do not send data today
def pis_Not_Send_Data(listOfPIs):
        now = datetime.datetime.now()
        today = now.strftime("%m-%d-%Y")
        now = now.strftime("%Y-%m-%d %H:%M")
        #the path the received tables placed in the central server      
        path = "/home/pi/Buffer/"
        #The list Pis which do not send data will be save in a file
        myfile = open("ListPIs.txt",'a+')
        myfile.write("\nPis which do not send data today: " + now)
        pisNotSendData = []
        for pi in listOfPIs:
                #the file name is the combination of Pi's MAC and current date
                fname = str(pi[0]) + today
                #Checks if the file starts with combination of MAC and current date exist in the directory
                for i in os.listdir(path):
                         if os.path.isfile(os.path.join(path,i)) and fname in i:
                                break
                #if it doesn't add to the list of pis who do not send data
                else:
                       pisNotSendData.append(str(pi[0]))
        #if the list is not empty add the content to the file
        if pisNotSendData:
		for pi in pisNotSendData:
                        myfile.write("\n" + str(pi))
        myfile.close()

#A metho that returns list of registerd pis in the central server
def pi_List():
        connectionDB = mdb.connect("localhost", "urban", "basketphone", "sicspi")
        cur = connectionDB.cursor()
        selectQuery = """SELECT EthMAC from PI"""
        cur.execute(selectQuery)
        rows = cur.fetchall()
        connectionDB.commit()
        connectionDB.close()
        return rows


if __name__ == "__main__":
    main()

