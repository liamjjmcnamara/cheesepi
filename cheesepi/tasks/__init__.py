
from cheesepi.tasks.task import Task
from cheesepi.tasks.dash import Dash
from cheesepi.tasks.dns import DNS
from cheesepi.tasks.dummy import Dummy
from cheesepi.tasks.httping import Httping
from cheesepi.tasks.iperf import iPerf
from cheesepi.tasks.mtr import MTR
from cheesepi.tasks.ping import Ping
from cheesepi.tasks.status import Status
from cheesepi.tasks.throughput import Throughput
from cheesepi.tasks.traceroute import Traceroute
from cheesepi.tasks.upgrade_code import Upgradecode
from cheesepi.tasks.upload import Upload
from cheesepi.tasks.wifi import Wifi

try:
    from cheesepi.tasks.update_tasks import Updatetasks
    from cheesepi.tasks.beacon import Beacon
except ImportError as exception:
    print("Warning: Problems importing Beacon/Updatetasks, " +
          "python Twisted probably not installed. {}".format(exception))
