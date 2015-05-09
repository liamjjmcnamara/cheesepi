#!/usr/bin/env python

from cStringIO import StringIO
import requests
import tarfile
import sys

install_dir = "/usr/local"
print "Downloading a CheesePi install into "+install_dir+"..."

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

lastmodified = response.headers['last-modified']
#print lastmodified

# if we have downloaded since it was updated, do nothing
response = requests.get(code_url)

fd = StringIO(response.content)
tfile = tarfile.open(mode="r:gz", fileobj=fd)

try:
	# should actually do this into /usr/local (or the correct cheesepi directory)
	tfile.extractall(install_dir)

	sys.path.append(install_dir)
	import cheesepi
	# record that we have just updated the code
	cheesepi.config.set_last_updated()
except OSError:
	print "Error: Can't untar the .tar.gz, you probably do not have permission, try sudo"
	exit(1)
