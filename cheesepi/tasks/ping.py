import os
import re
import sys
import time
import logging
import socket
import statistics

import cheesepi
from cheesepi.tasks.task import Task

LOGGER = cheesepi.config.get_logger(__name__)

class Ping(Task):

    # construct the process and perform pre-work
    def __init__(self, dao, spec):
        cheesepi.tasks.task.Task.__init__(self, dao, spec)
        self.spec['taskname'] = "ping"
        if 'landmark' not in self.spec:
            self.spec['landmark'] = "www.sics.se"
        if 'ping_count' not in self.spec:
            self.spec['ping_count'] = 10
        if 'packet_size' not in self.spec:
            self.spec['packet_size'] = 64
        try:
            socket.gethostbyname(self.spec['landmark']) # we dont care, just populate the cache
        except:
            pass # record ping failure later

    # actually perform the measurements, no arguments required
    def run(self):
        LOGGER.info("Pinging: %s @ %f, PID: %d", self.spec['landmark'], time.time(), os.getpid())
        self.measure()

    # measure and record funtion
    def measure(self):
        start_time = cheesepi.utils.now()
        op_output = self.perform(self.spec['landmark'], self.spec['ping_count'],
                                 self.spec['packet_size'])
        end_time = cheesepi.utils.now()

        LOGGER.debug(op_output)
        if op_output is not None: # we succeeded
            self.parse_output(op_output.decode("utf-8"), self.spec['landmark'], start_time, end_time,
                              self.spec['packet_size'], self.spec['ping_count'])
        self.dao.write_op(self.spec['taskname'], self.spec)

    #ping function
    def perform(self, landmark, ping_count, packet_size):
        packet_size -= 8 # change packet size to payload length!
        command = "ping -c {} -s {} {}".format(ping_count, packet_size, landmark)
        logging.info("Executing: %s", command)
        LOGGER.info(command)
        self.spec['return_code'], output = self.execute(command)
        LOGGER.info(output)

        if self.spec['return_code'] == 0:
            return output
        if self.spec['return_code'] == 68:
            self.spec['error'] = "Unknown host"
        elif self.spec['return_code'] == 2:
            self.spec['error'] = "No response"
        return None

    # read the data from ping and reformat for database entry
    def parse_output(self, data, landmark, start_time, end_time, packet_size, ping_count):
        self.spec["start_time"] = start_time
        self.spec["end_time"] = end_time
        delays = []

        lines = data.split("\n")
        first_line = lines.pop(0).split()
        self.spec["destination_domain"] = first_line[1]
        self.spec["destination_address"] = re.sub("[()]", "", str(first_line[2]))

        delays = [-1.0] * ping_count# initialise storage
        for line in lines:
            print("line: "+line)
            if "time=" in line: # is this a PING return line?
                # does the following string wrangling always hold? what if not "X ms" ?
                # also need to check whether we are on linux-like or BSD-like ping
                if "icmp_req" in line: # BSD counts from 1
                    sequence_num = int(re.findall(r'icmp_.eq=[\d]+ ', line)[0][9:-1]) -1
                elif "icmp_seq" in line: # Linux counts from 0
                    sequence_num = int(re.findall(r'icmp_.eq=[\d]+ ', line)[0][9:-1])
                else:
                    logging.error("ping parse error: %s", line)
                    sys.exit(1)
                delay = re.findall('time=.*? ms', line)[0][5:-3]
                # only save returned pings!
                delays[sequence_num-1] = float(delay)
            elif "packet loss" in line:
                loss = re.findall(r'[\d]+% packet loss', line)[0][:-13]
                self.spec["packet_loss"] = float(loss)
            elif "min/avg/max/" in line:
                fields = line.split()[3].split("/")
                self.spec["minimum_RTT"] = float(fields[0])
                self.spec["average_RTT"] = float(fields[1])
                self.spec["maximum_RTT"] = float(fields[2])
                self.spec["stddev_RTT"] = float(fields[3])

        print(delays)
        self.spec['delays'] = str(delays)
        self.spec["minimum_RTT"] = min(delays)
        self.spec["average_RTT"] = statistics.mean(delays)
        self.spec["maximum_RTT"] = max(delays)
        self.spec['uploaded'] = self.spec['packet_size'] * self.spec['ping_count']
        self.spec['downloaded'] = 8 * self.spec['ping_count']

if __name__ == "__main__":
    # general logging here? unable to connect etc
    dao = cheesepi.storage.get_dao()
    spec = {'landmark':'www.sics.se'}
    ping_task = Ping(dao, spec)
    ping_task.run()
