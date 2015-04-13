#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import datetime

def main():
	host = "localhost"
	user = "urban"
	db = "sicspi"

	pw = raw_input("Please supply your password:\n")
	connectionDB = mdb.connect(host, user, pw, db)

	with connectionDB:
		cur = connectionDB.cursor()
		
		cur.execute("DELETE FROM Ping WHERE true")
		cur.execute("DELETE FROM Operation WHERE true")
		cur.execute("DELETE FROM Central_DNS WHERE true")
		cur.execute("DELETE FROM Connection WHERE true")
		cur.execute("DELETE FROM User WHERE true")
		cur.execute("DELETE FROM PI WHERE true")
		
		cur.execute("ALTER TABLE PI AUTO_INCREMENT = 1")
		cur.execute("ALTER TABLE Connection AUTO_INCREMENT = 1")
		cur.execute("ALTER TABLE Central_DNS AUTO_INCREMENT = 1")
		cur.execute("ALTER TABLE Operation AUTO_INCREMENT = 1")

	connectionDB.commit()
	connectionDB.close()


if __name__ == "__main__":
    main()
