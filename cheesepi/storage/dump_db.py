#!/usr/bin/env python

import tempfile
import gzip
import cheesepi
import requests


dump_url = "http://cheesepi.sics.se/upload.py"

def upload_dump():
    pass

def my_callback(monitor):
    # Your callback function
    print monitor.bytes_read

def perform_database_dump():
    dao = cheesepi.config.get_dao()

    last_updated = cheesepi.config.get_last_updated(dao)
    dao.dump(last_updated)

    files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}

    r = requests.post(dump_url, files=files)
    print r.text


if __name__ == "__main__":
    perform_database_dump()

