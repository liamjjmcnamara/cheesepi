
Introduction to the source code for the CheesePi measurement platform

Install
-----------------

To obtain the CheesePi dsitribution, simply install the python module:
``sudo pip install cheesepi``

This will download and install the modules and programs in your python module directory.



Starting CheesePi
-----------------

There are three main components, the influxdb server, the measurement dispatcher and
the dashboard. The influxdb server stores measurement results, the dispatcher regularly
performs the measurement tasks and stores their results in the influxdb. To view the
results, the dashboard can optionally be started.

Start the storage server:
~~~~~~~~~~~~~~~~~~~~~~
``cheesepi start influxdb``

Start measuring
~~~~~~~~~~~~~~~~~~~~~~
``cheesepi start dispatcher``

Start the dashboard webserver
~~~~~~~~~~~~~~~~~~~~~~
``cheesepi start dashboard``

This command starts a webserver on the localhost that will display the collected data.
Browse to http://localhost:8080 to view this dashboard.


Configuring
-----------------

Location of configuration files
~~~~~~~~~~~~~~~~~~~~~~
``cheesepi status``

Schedule
~~~~~~~~~~~~~~~~~~~~~~


Configuration
~~~~~~~~~~~~~~~~~~~~~~



Included modules
-----------------

The speedtest module is from https://pypi.python.org/pypi/speedtest-cli/
Which is under license: Apache License, Version 2.0

