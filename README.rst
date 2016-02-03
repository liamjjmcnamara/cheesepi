
Introduction to the source code for the CheesePi measurement platform

Install
-----------------

To obtain the CheesePi dsitribution, simply install the python module:

``$ sudo pip install cheesepi``

This will download and install the modules and programs in your python module
directory.



Starting CheesePi
-----------------

There are three main components, the influxdb server, the measurement
dispatcher and the dashboard. The influxdb server stores measurement results,
the dispatcher regularly performs the measurement tasks and stores their
results in the influxdb. To view the results, the dashboard can optionally be
started.

Start the storage server:
~~~~~~~~~~~~~~~~~~~~~~
``$ cheesepi start influxdb``

Start measuring
~~~~~~~~~~~~~~~~~~~~~~
``$ cheesepi start dispatcher``

Start the dashboard webserver
~~~~~~~~~~~~~~~~~~~~~~
``$ cheesepi start dashboard``

This command starts a webserver on the localhost that will display the
collected data. Browse to http://localhost:8080 to view this dashboard.



Customising behaviour
-----------------
There are two main files for customising the behaviour of CheesePi, a main
configuration file and a schedule of tasks to execute. The main configuration
file *cheesepi.conf* controls the level of logging, whether to auto-upgrade the
code, which central sever to use, etc. The schedule file *schedule.dat*
specifies which tasks the system will perform. The location of both files from
your installation can be found with the following command:

``$ cheesepi status``

Local copies are these files are generated. Any change will stay local to your
installation and not be overwritten by software upgrades. If you delete your
local copy, a new default copy will be generated.

Configuration
~~~~~~~~~~~~~~~~~~~~~~
The configuration file format is rather simple, key value pairs of strings are
set with the format:

*key = value*

Lines can be commmented out with a *#*.


Schedule
~~~~~~~~~~~~~~~~~~~~~~

The schedule file format is of one JSON sting (http://www.w3schools.com/json/)
per line. Each JSON object represents a *measurement task*, the only required 
field is *taskname*, all others are option parameters to the task. Lines can
be commented out with a *#*.



Included modules
-----------------

The speedtest module is from https://pypi.python.org/pypi/speedtest-cli/
Which is under license: Apache License, Version 2.0

