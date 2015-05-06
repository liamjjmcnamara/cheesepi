#!/usr/bin/env python

import sys
import zlib
import io
import zipfile
import StringIO
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
    #files = {'file': ('unusedfilename.tar.gz', zlib.compress(dump_data)), }
    #fd = io.BytesIO(dump_data)
    #zdata = zipfile.ZipFile(fd)
    fd = tempfile.TemporaryFile()
    zfd = zipfile.ZipFile(fd,'w', zipfile.ZIP_DEFLATED)
    zfd.writestr("file.z",dump_data)
    fd.flush()
    fd.seek(0)

    #buff = StringIO.StringIO()
    #zip_archive = zipfile.ZipFile(buff, mode='w')
    #zip_archive.writestr("file.dat",dump_data)
    #zip_archive.close()
    
    #zfd = zipfile.ZipFile(StringIO.StringIO(), 'a')
    #zfd.writestr("filename.z",dump_data)
    #zfd.close()
    files = {'file': ('archive.z', fd), }

    r = requests.post(dump_url, data=parameters, files=files)
    print r.text
    #fd.close()


if __name__ == "__main__":
    perform_database_dump()

