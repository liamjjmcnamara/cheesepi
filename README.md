
Introduction to the source code for the CheesePi measurement platform

# Install

To obtain a CheesePi distribution, simply download:
`http://cheesepi.sics.se/files/cheesepi.tar.gz`

Then unpack the archive and run the "./install/install.sh" script.
This will install CheesePi into the specified directory, by default:  */usr/local/cheesepi*. 

The install script that will ensure you have the correct programs and python
modules installed. It will also cause the local database server (currently
InfluxDB) and a webserver (for the dashboard) to be run upon start up (through inittab).


