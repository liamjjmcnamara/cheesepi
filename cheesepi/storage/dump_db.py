#!/usr/bin/env python

import sys
import zlib
import io
import zipfile
import StringIO
import requests

sys.path.append("/usr/local/")
import cheesepi

dump_url = "http://cheesepi.sics.se/upload.py"


def perform_database_dump():
    dao = cheesepi.config.get_dao()
    ethmac = cheesepi.utils.getCurrMAC()

    last_updated = cheesepi.config.get_last_updated(dao)
    dump_data = dao.dump(last_updated)

    parameters = {'ethmac': ethmac}
    #files = {'file': ('unusedfilename.tar.gz', zlib.compress(dump_data)), }

    #fd = io.BytesIO(dump_data)
    #zdata = zipfile.ZipFile(fd)
    
    zfd = zipfile.ZipFile(StringIO.StringIO(), 'a')
    zfd.writestr("filename.z",dump_data)
    zfd.close()
    files = {'file': ('unusedfilename.tar.gz', zfd), }

    r = requests.post(dump_url, data=parameters, files=files)
    print r.text


if __name__ == "__main__":
    perform_database_dump()

