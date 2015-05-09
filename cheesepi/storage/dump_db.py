#!/usr/bin/env python

import sys
import zipfile
import tempfile
import requests

sys.path.append("/usr/local/")
import cheesepi

dump_url = "http://cheesepi.sics.se/upload.py"


def perform_database_dump():
    dao = cheesepi.config.get_dao()

    last_updated = cheesepi.config.get_last_updated(dao)
    dump_data = dao.dump(last_updated)
    ethmac = cheesepi.utils.getCurrMAC()
    parameters = {'ethmac': ethmac}

    # make a temp file that dies on running out of scope
    fd = tempfile.TemporaryFile()
    # make a zipfile object with this file handle
    zfd = zipfile.ZipFile(fd,'w', zipfile.ZIP_DEFLATED)
    zfd.writestr("file.z",dump_data)
    fd.flush()
    fd.seek(0) # flush and reset file handle

    files = {'file': ('archive.z', fd), }
    r = requests.post(dump_url, data=parameters, files=files)
    print r.text
    #fd.close()


if __name__ == "__main__":
    perform_database_dump()
    # remember when we last successfully dumped our data
    cheesepi.config.set_last_dumped()
