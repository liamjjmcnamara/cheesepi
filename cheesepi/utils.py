""" Copyright (c) 2015, Swedish Institute of Computer Science
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
  * Neither the name of The Swedish Institute of Computer Science nor the
    names of its contributors may be used to endorse or promote products
    derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE SWEDISH INSTITUTE OF COMPUTER SCIENCE BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Authors: ljjm@sics.se
Testers:
"""

import os
import sys
import hashlib
import uuid
import time
import random
import urllib
import argparse
from subprocess import call

import cheesepi
import cheesepi.dispatcher as dispatcher
#from cheesepi.tasks import *

logger = cheesepi.config.get_logger(__name__)

def console_script():
    """Command line tool, installed through setup.py"""
    commands = ['start', 'stop', 'status', 'reset', 'upgrade']

    parser = argparse.ArgumentParser(prog='cheesepi')
    parser.add_argument('command', metavar='COMMAND', choices=commands, nargs='?',
                        help="Perform one of the following commands: " + str(commands))
    args = parser.parse_args()

    if args.command == "status":
        show_status()
    elif args.command == "start":
        start_dispatcher()
    elif args.command == "stop":
        stop_dispatcher()
    elif args.command == "reset":
        reset_install()
    elif args.command == "upgrade":
        upgrade_install()
    elif args.command == "list":
        list_data(args.option)
    else:
        parser.error("Unknown COMMAND")

def show_status():
    """Just print the location of important CheesePi dirs/files"""
    schedule_file = os.path.join(cheesepi.config.cheesepi_dir, cheesepi.config.get('schedule'))
    print("Status of CheesePi install (version {})\n--".format(cheesepi.config.version()))
    print("Install dir:\t{}".format(cheesepi.config.cheesepi_dir))
    #print("Log file:\t{}".format(cheesepi.config.log_file))
    print("Config file:\t{}".format(cheesepi.config.config_file))
    print("Schedule file:\t{}".format(schedule_file))
    print("")
    ip_addr = cheesepi.utils.get_IP()
    port = cheesepi.config.get_dashboard_port()
    print("Dashboard URL: http://{}:{}".format(ip_addr, port))

def list_data(task="ping"):
    dao = cheesepi.storage.get_dao()
    print(dao.read_op(task))

def start_dispatcher():
    print("Starting the dispatcher...")
    dispatcher.start()

def stop_dispatcher():
    print("Stoping the dispatcher...")
    dispatcher.stop()
    sys.exit(1)

# def copy_influx_config(influx_config):
    # """Copy the default influx config to a local copy (probably in $HOME)"""
    # print("Warning: making local config: {}".format(influx_config))
    # storage_dir = "/var/lib/influxdb"
    # if not os.path.exists(storage_dir):
        # print("Warning: Default InfluxDB storage dir {} does not exist!".format(storage_dir))
        # print("Make the directory and user editable:\n sudo mkdir {} && chown $USER {}".format(storage_dir, storage_dir))
    # influx_dir = cheesepi.config.cheesepi_dir + "/bin/tools/influxdb"
    # default_config = os.path.join(influx_dir, "config.toml")
    # print("Warning: copying from default config: {}".format(default_config))
    # cheesepi.config.copyfile(default_config, influx_config, replace={"INFLUX_DIR":influx_dir})

def test_execute(cmd_array):
    """Return true if cmd_array can execute"""
    try:
        call(cmd_array)
        return True
    except:
        return False

# def find_influx_exe():
    # """See which influxdb we should use"""
    # config_path = cheesepi.config.get("database_exe")
    # if config_path: # if database exectable was set in config file
        # return config_path
    # elif (test_execute(["influxdb", "-h"])):
        # return "influxdb"
    # else:
        # if isARM():
          # return cheesepi.config.cheesepi_dir+"/bin/tools/influxdb/influxdb.arm"
        # else:
          # print("Error: Can't find a valid InfluxDB binary")
          # print("Install InfluxDB and then set the binary's path as 'database_exe' in cheesepi.conf")
          # sys.exit(2)

# def control_storage(action):
    # """Start or stop InfluxDB, either the bundled or the system version"""
    # storage_dir = "/var/lib/influxdb"
    # if not os.path.exists(storage_dir):
        # print("Warning: Default InfluxDB storage dir {} does not exist!".format(storage_dir))
        # print("Will try to make it...")
        # # try to make the dir
        # try:
          # os.makedirs(storage_dir)
        # except Exception as e:
          # print("Tried to make the directory, but it failed: {}".format(e))
          # sys.exit(3)

    # if action=='start':
        # print("Starting InfluxDB...")
        # home_dir = os.path.expanduser("~")
        # influx_config = os.path.join(home_dir, ".influxconfig.toml")
        # # test if we have already made the local config file
        # if not os.path.isfile(influx_config):
          # copy_influx_config(influx_config)
        # influx=find_influx_exe()
        # # start the influx server
        # print("Running: "+influx+" -config="+influx_config)
        # try:
          # call([influx, "-config="+influx_config])
        # except Exception as e:
          # msg = "Problem executing influxdb command {} -config={}: {}".format(influx, influx_config, e)
          # msg += "\nCheck PATH inclusion of system and python 'bin' directories"
          # print(msg)
          # logger.error(msg)
    # else:
        # print("Error: action not yet implemented!")

# def control_dashboard(action):
    # """Start or stop the webserver that hosts the dashboard"""
    # if action=='start':
        # print("Starting the dashboard...")
        # cheesepi.bin.webserver.webserver.setup_server()
    # else:
        # print("Error: action not yet implemented!")

# def control_all(action):
    # pool = multiprocessing.Pool(processes=3)
    # #pool.apply_async(control_storage, [action])
    # time.sleep(3) # allow spoolup and config generation
    # pool.apply_async(control_dispatcher, [action])
    # pool.apply_async(control_dashboard, [action])
    # pool.close()
    # pool.join()

def reset_install():
    """Wipe all local changes to schedule, config"""
    home_dir = os.path.expanduser("~")
    influx_config = os.path.join(home_dir, ".influxconfig.toml")
    copy_influx_config(influx_config)
    cheesepi.config.ensure_default_config(True)

def upgrade_install():
    """Try and pull new version of the code from PyPi"""
    import cheesepi.tasks
    upgrade_task = cheesepi.tasks.Upgradecode()
    upgrade_task.run()

def make_series():
    """Ensure that database contains series grafana and cheesepi"""
    dao = cheesepi.storage.get_dao()
    # TODO: dont make if already exists
    dao.make_database("cheesepi")
    dao.make_database("grafana")

def build_json(dao, json_str):
    """Build a Task object out of a JSON string spec"""
    import json
    spec = json.loads(json_str)
    return build_task(dao, spec)

def build_task(dao, spec):
    if not 'taskname' in spec:
        logger.error("No 'taskname' specified!")
        return None

    spec['taskname'] = spec['taskname'].lower()
    if spec['taskname'] == 'ping':
        return cheesepi.tasks.ping.Ping(dao, spec)
    if spec['taskname'] == 'httping':
        return cheesepi.tasks.Httping(dao, spec)
    if spec['taskname'] == 'traceroute':
        return cheesepi.tasks.Traceroute(dao, spec)
    if spec['taskname'] == 'dash':
        return cheesepi.tasks.Dash(dao, spec)
    # if spec['taskname'] == 'dns':
        # return cheesepi.tasks.dns.DNS(dao, spec)
    if spec['taskname'] == 'throughput':
        return cheesepi.tasks.Throughput(dao, spec)
    if spec['taskname'] == 'iperf':
        return cheesepi.tasks.iPerf(dao, spec)
    if spec['taskname'] == 'mtr':
        return cheesepi.tasks.MTR(dao, spec)
    if spec['taskname'] == 'upload':
        return cheesepi.tasks.Upload(dao, spec)
    if spec['taskname'] == 'status':
        return cheesepi.tasks.Status(dao, spec)
    if spec['taskname'] == 'wifi':
        return cheesepi.tasks.Wifi(dao, spec)
    if spec['taskname'] == 'dummy':
        return cheesepi.tasks.Dummy(dao, spec)
    if spec['taskname'] == 'upload':
        return cheesepi.tasks.Upload(dao, spec)
    if spec['taskname'] == 'upgradecode':
        return cheesepi.tasks.Upgradecode(dao, spec)
    if spec['taskname'] == 'beacon':
        try:
            return cheesepi.tasks.Beacon(dao, spec)
        except: # return dummy Task
            return cheesepi.tasks.Task(dao)
    elif spec['taskname'] == 'updatetasks':
        try:
            return cheesepi.tasks.Updatetasks(dao, spec)
        except:
            return cheesepi.tasks.Task(dao)
    else:
        raise Exception('Task name not specified! '+str(spec))

# time functions
def now():
    return time.time()
    #return int(datetime.datetime.utcnow().strftime("{}"))

def isARM():
    import platform
    if "arm" in platform.machine():
        return True
    return False

# logging facilities
def write_file(ret, start_time, ethmac):
    filename = "./"+ethmac+str(start_time)+".txt"
    fd = open(filename, 'w')
    fd.write(ret)
    fd.close()

def get_MAC():
    """Return the MAC of this device's first NIC"""
    return str(hex(uuid.getnode()))[2:]

def get_host_id():
    """Return this host's ID"""
    return str(hashlib.md5(get_MAC().encode("utf-8")).hexdigest())

#get our currently used MAC address
def getCurrMAC():
    ret = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])
    return ret

def resolve_if(interface):
    """Get the IP address of an interface"""
    addr = "127.0.0.1" # a bad default value (will only work locally)
    try:
        import netifaces
        addr_type = 2 # 2=AF_INET, 30=AF_INET6
        addr = netifaces.ifaddresses(interface)[addr_type][0]['addr']
    except Exception: # netifaces failed
        import socket
        # try to use the fully qualified domain name
        addr = socket.getfqdn()
    return addr

def get_IP():
    """Try to get this host's active address"""
    interfaces = ["eth0", "en0", "wlan0"]
    # apppend all interfaces on this host
    for interface in interfaces:
        ip = resolve_if(interface)
        if ip != None: # we have a valid IP
        	return ip
    # unknown IP
    return "127.0.0.1"

def get_SA():
    """Get our percieved remote source address"""
    try:
        ret = urllib.urlopen('http://ip.42.pl/raw').read()
    except Exception as e: # We may be offline
        logger.error("Unable to request ip.42.pl server's view of our IP, we may be offline: {}".format(e))
        return "0.0.0.0"
    return ret

def get_temperature():
    """Return the current temperature sensor, if possible"""
    filename = "/sys/class/thermal/thermal_zone0/temp"
    try:
        f = open(filename, 'r')
        data = f.read()
        return float(data.strip())
    except:
        pass
    return None

def get_status():
    status = {}
    status['tcp'] = random.randint(0, 100)
    status['udp'] = random.randint(0, 100)
    status['time'] = time.time()
    status['jitter'] = -1
    status['bandwidth'] = random.randint(0, 100)
    return status

#
# Simple statistics to avoid numpy
#
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)


def sumsq(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss


def stdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = sumsq(data)
    pvar = ss/n # the population variance
    return pvar**0.5
