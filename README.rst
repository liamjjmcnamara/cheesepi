
Introduction to the source code for the CheesePi measurement platform

# Install

To obtain a CheesePi distribution, simply download:
`http://cheesepi.sics.se/files/cheesepi.tar.gz`

Then unpack the archive and run the "./install/install.sh" script.
This will install CheesePi into the specified directory, by default:  */usr/local/cheesepi*. 

The install script that will ensure you have the correct programs and python
modules installed. It will also cause the local database server (currently
InfluxDB) and a webserver (for the dashboard) to be run upon start up (through inittab).

The CheesePi python module will be installed at CHEESEPILIB=INSTALL_DIR/cheesepilib/cheesepilib/
The CheesePi configuration file is at $CHEESEPILIB/cheesepi.conf and the measurement task
schedule file is at $CHEESEPILIB/schedule.dat


The speedtest module is from https://pypi.python.org/pypi/speedtest-cli/
Which is under license: Apache License, Version 2.0

