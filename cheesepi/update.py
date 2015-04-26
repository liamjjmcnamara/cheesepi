#!/usr/bin/env python

from cStringIO import StringIO
import requests
import tarfile

# Location of the most recent release of the CheesePi code
url = "http://cheesepi.sics.se/files/cheesepi.tar.gz"

response = None
try:
    response = requests.head(url=url)
except Exception as e:
    print "Error: Could not make request to CheesePi server "+url+": "+str(e)
    exit(1)

if response.status_code!=200:
    print "Error: file %s was not available on server" % url

print(response.headers)
lastmodified = response.headers['last-modified']
print lastmodified

# if we have downloaded since it was updated, do nothing
response = requests.get(url)

#tar = tarfile.open(mode= "r:gz", fileobj = StringIO(response.content)y)
#results = gzip.GzipFile(fileobj=StringIO(response.content))

fd = StringIO(response.content)
tfile = tarfile.open(mode="r:gz", fileobj=fd)
tfile.extractall('/tmp')

