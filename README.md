
Introduction to the source code for the CheesePi measurement platform

# Install

To obtain a CheesePi distribution, simply download:
`http://cheesepi.sics.se/files/cheesepi.tar.gz`

Then unpack the archive into the  */usr/local/cheesepi* directory. 

There is an install script that will ensure you have the correct 
programs and python modules installed. It will also cause the database
server (currently InfluxDB) and webserver (for the dashboard) to be run
upon start up. Simply run it be executing:

`$ /usr/local/cheesepi/install/install.sh`

