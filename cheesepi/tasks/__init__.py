
from cheesepi.tasks.Task import Task
from cheesepi.tasks.Dummy import Dummy
from cheesepi.tasks.Upload import Upload
from cheesepi.tasks.Upgradecode import Upgradecode
from cheesepi.tasks.Status import Status
from cheesepi.tasks.Ping import Ping
from cheesepi.tasks.Httping import Httping
from cheesepi.tasks.Traceroute import Traceroute
from cheesepi.tasks.MTR import MTR
from cheesepi.tasks.Dash import Dash
from cheesepi.tasks.DNS import DNS
from cheesepi.tasks.Throughput import Throughput
from cheesepi.tasks.iPerf import iPerf
from cheesepi.tasks.Wifi import Wifi

try:
	from cheesepi.tasks.Updatetasks import Updatetasks
	from cheesepi.tasks.Beacon import Beacon
except Exception as e:
	print("Warning: Problems importing Beacon/Updatetasks, python Twisted probably not installed. {}".format(e))
