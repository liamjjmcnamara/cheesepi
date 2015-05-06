#!/usr/bin/env python

import sys
import tempfile
import gzip
import requests

sys.path.append("/usr/local/")
import cheesepi

dump_url = "http://cheesepi.sics.se/upload.py"


def perform_database_dump():
    dao = cheesepi.config.get_dao()
    ethmac = cheesepi.utils.getCurrMAC()

    last_updated = cheesepi.config.get_last_updated(dao)
    dump_data = dao.dump(last_updated)
    print ethmac

    data = {'ethmac': ethmac}
    files = {'file': ('unusedfilename.tar.gz', dump_data), }

    r = requests.post(dump_url, data=data, files=files)
    print r.text


if __name__ == "__main__":
    perform_database_dump()

