
from Task import Task
from Dummy import Dummy
from Upload import Upload
from Upgradecode import Upgradecode
from Status import Status
from Ping import Ping
from Httping import Httping
from Traceroute import Traceroute
from MTR import MTR
from Dash import Dash
from DNS import DNS
from Throughput import Throughput
from iPerf import iPerf
from Wifi import Wifi

try:
	from Updatetasks import Updatetasks
	from Beacon import Beacon
except Exception as e:
	print "Warning: Problems importing Beacon/Updatetasks, python Twisted probably not installed. %s" % e

