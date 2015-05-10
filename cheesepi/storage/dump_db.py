#!/usr/bin/env python

import sys
import tarfile
import tempfile
import StringIO
import requests

sys.path.append("/usr/local/")
import cheesepi

dump_url = "http://cheesepi.sics.se/upload.py"


def perform_database_dump():
    dao = cheesepi.config.get_dao()
    last_dumped = cheesepi.config.get_last_dumped(dao)

    print "Last dumped: "+str(last_dumped)
    dumped_tables = dao.dump(last_dumped)
    ethmac = cheesepi.utils.getCurrMAC()
    parameters = {'ethmac': ethmac}

    # make a temp file that dies on running out of scope
    fd = tempfile.TemporaryFile()
    # make a zipfile object with this file handle
    tar = tarfile.open(fileobj=fd, mode="w:gz")
    for table in dumped_tables.keys():
        print table
        table_info = tarfile.TarInfo(name=table+".json")
        table_info.size=len(dumped_tables[table])
        tar.addfile(table_info, StringIO.StringIO(dumped_tables[table]))
    tar.close()
    fd.flush()
    fd.seek(0) # flush and reset file handle, so it can be read for POST

    files = {'file': ('archive.tgz', fd), }
    r = requests.post(dump_url, data=parameters, files=files)
    print r.text
    #fd.close()
    # remember when we last successfully dumped our data
    cheesepi.config.set_last_dumped()


if __name__ == "__main__":
    perform_database_dump()
