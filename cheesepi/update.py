#!/usr/bin/env python

from cStringIO import StringIO
import requests
import tarfile
import sys

sys.path.append("/usr/local")
import cheesepi

# Location of the most recent release of the CheesePi code
code_url = "http://cheesepi.sics.se/files/cheesepi.tar.gz"

response = None
try:
    response = requests.head(url=code_url)
except Exception as e:
    print "Error: Could not make request to CheesePi server "+code_url+": "+str(e)
    exit(1)

if response.status_code!=200:
    print "Error: file %s was not available on server" % code_url
    exit(1)

print(response.headers)
lastmodified = response.headers['last-modified']
print lastmodified

# if we have downloaded since it was updated, do nothing
response = requests.get(code_url)

#tar = tarfile.open(mode= "r:gz", fileobj = StringIO(response.content)y)
#results = gzip.GzipFile(fileobj=StringIO(response.content))

fd = StringIO(response.content)
tfile = tarfile.open(mode="r:gz", fileobj=fd)

# should actually do this into /usr/local (or the correct cheesepi directory)
tfile.extractall('/tmp')

# record that we have just updated the code
cheesepi.config.set_last_updated()
