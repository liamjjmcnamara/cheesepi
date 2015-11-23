import sys
import time
import os
import re
import logging
import socket
from subprocess import Popen, PIPE

sys.path.append("/usr/local/")
import cheesepi

from Task import Task

class Ping(Task):

    def __init__(self, dao, parameters):
        self.taskname    = "ping"
        self.dao         = dao
        self.landmark    = parameters['landmark']
        self.ping_count  = 10 #parameters['ping_count']
        self.packet_size = 64 #parameters['packet_size']
        socket.gethostbyname(self.landmark) # we dont care, just populate the cache

    def run(self):
        print "Pinging: %s @ %f, PID: %d" % (self.landmark, time.time(), os.getpid())
        self.measure(self.landmark, self.ping_count, self.packet_size)
        time.sleep(5)

    #main measure funtion
    def measure(self, landmark, ping_count, packet_size):
        start_time = cheesepi.utils.now()
        op_output = self.perform(self.landmark, ping_count, packet_size)
        end_time = cheesepi.utils.now()
        print op_output

        parsed_output = self.parse_output(op_output, landmark, start_time, end_time, packet_size, ping_count)
        self.dao.write_op("ping", parsed_output)

    #ping function
    def perform(self, landmark, ping_count, packet_size):
        packet_size -= 8 # change packet size to payload length!
        execute = "ping -c %s -s %s %s"%(ping_count, packet_size, landmark)
        logging.info("Executing: "+execute)
        print execute
        result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        ret = result.stdout.read()
        result.stdout.flush()
        return ret

    #read the data from ping and reformat for database entry
    def parse_output(self, data, landmark, start_time, end_time, packet_size, ping_count):
        ret = {}
        ret["landmark"]    = landmark
        ret["start_time"]  = start_time
        ret["end_time"]    = end_time
        ret["packet_size"] = int(packet_size)
        ret["ping_count"]  = int(ping_count)
        delays=[]

        lines = data.split("\n")
        first_line = lines.pop(0).split()
        ret["destination_domain"]  = first_line[1]
        ret["destination_address"] = re.sub("[()]", "", str(first_line[2]))

        delays = [-1.0] * ping_count# initialise storage
        for line in lines:
            if "time=" in line: # is this a PING return line?
                # does the following string wrangling always hold? what if not "X ms" ?
                # also need to check whether we are on linux-like or BSD-like ping
                if "icmp_req" in line: # BSD counts from 1
                    sequence_num = int(re.findall('icmp_.eq=[\d]+ ',line)[0][9:-1]) -1
                elif "icmp_seq" in line: # Linux counts from 0
                    sequence_num = int(re.findall('icmp_.eq=[\d]+ ',line)[0][9:-1])
                else:
                    logging.error("ping parse error:"+line)
                    exit(1)
                delay = re.findall('time=.*? ms',line)[0][5:-3]
                #print sequence_num,delay
                # only save returned pings!
                delays[sequence_num]=float(delay)
        ret['delays'] = str(delays)

        # probably should not reiterate over lines...
        for line in lines:
            if "packet loss" in line:
                loss = re.findall('[\d]+% packet loss',line)[0][:-13]
                ret["packet_loss"] = float(loss)
            elif "min/avg/max/" in line:
                fields = line.split()[3].split("/")
                ret["minimum_RTT"] = float(fields[0])
                ret["average_RTT"] = float(fields[1])
                ret["maximum_RTT"] = float(fields[2])
                ret["stddev_RTT"]  = float(fields[3])
        return ret

