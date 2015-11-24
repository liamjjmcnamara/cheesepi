import time
import os
import sys
import platform
import re
from subprocess import Popen, PIPE

sys.path.append("/usr/local/")
import Task
import cheesepi.utils

class Traceroute(Task.Task):

    def __init__(self, dao, parameters):
        self.taskname = "traceroute"
        self.dao = dao
        self.landmark = parameters['landmark']

    def toDict(self):
        return {'taskname' :self.taskname,
                'landmark' :self.landmark,
                }

    def run(self):
        print "Tracerouting: %s PID: %d" % (self.landmark, os.getpid())
        self.measure(self.landmark)
        time.sleep(4)


    def measure(self, landmark):
        hoplist = []
        #Extract the ethernet MAC address of the PI
        startTime = cheesepi.utils.now()
        output    = self.getData(landmark)
        endTime   = cheesepi.utils.now()
        #trc, hoplist = reformat(tracerouteResult, startTime, endTime)
        print output
        traceroute, hoplist = self.parse(output, startTime, endTime)
        self.insertData(self.dao, traceroute, hoplist)

    #Execute traceroute function
    def getData(self, target):
        #traceroute command"
        execute = "traceroute %s"%(target)
        #Executing the above shell command with pipe
        result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        ret = result.stdout.read()
        result.stdout.flush()
        return ret

    def parse_null(self, hop_count):
        return {'hop_count': hop_count,
            'domain1': "*", 'domain2': "*", 'domain3': "*",
            'ip1'    : "*", 'ip2'    : "*", 'ip3'    : "*",
            'delay1': -1, 'delay2': -1, 'delay3': -1, }

    #############################
    # Parse Linux command
    #

    def parse(self, data, start_time, end_time):
        lines = data.split("\n")
        traceroute = self.parse_destination(lines[0], start_time, end_time)
        hops=[]
        for line in lines[1:-1]:
            hop_count = int(line[:3].strip())
            hops.append(self.parse_hop(hop_count, line[4:]))
        print "hops: ",hops
        return traceroute, hops

    def parse_destination(self, destination, start_time, end_time):
        traceroute = {}
        fields = destination.split()
        traceroute['domain']     = fields[2]
        traceroute['ip']         = fields[3][1:-1]
        traceroute['start_time'] = start_time
        traceroute['end_time']   = end_time
        return traceroute

    def parse_hop(self, hop_count, host_line):
        """This does not yet deal with network problems"""
        hop={'hop_count':hop_count}
        retry="1" # string accumulator
        for match in re.finditer(r"\*|(([\w\.-]+) \(([\d\.]+)\)  ([\d\.ms ]+) )", host_line):
            if match.group(0)=="*": # found a non response
                hop['domain'+retry]="*"
                hop['ip'+retry]="*"
                hop['delay'+retry]="-1"
            else: # some host reploiued N times
                for delay in match.group(4).split("ms"):
                    hop['domain'+retry]= match.group(2)
                    hop['ip'+retry]    = match.group(3)
                    hop['delay'+retry] = delay
                    retry = str(int(retry)+1) # inc but keep as string
            retry = str(int(retry)+1) # inc but keep as string
        return hop


    #########################
    ## Mac traceroute
    ########################
    def parse_mac(self, data):
        hops=[]
        lines = data.split()
        lines.pop(0)
        hop_count=-1
        while (len(lines)>0):
            line = lines.pop(0)
            hop_count = int(line[:3].strip())
            print hop_count
            host_line = line[4:] # extract everything after hopcount
            host_fields = host_line.split()
            if len(host_fields)==3:
                hops.extend(self.parse_null(hop_count))
            elif len(host_fields)==8: # the same host responds for each retry
                hop_entries = self.parse_hop_1host(hop_count,host_fields)
                hops.extend(hop_entries)
            elif len(host_fields)==4: # multiple hosts respond at this hop
                retry2 = lines.pop(0)[4:] #pop the next 2 lines
                retry3 = lines.pop(0)[4:]
                hop_entries = self.parse_hop_3host(hop_count,host_line, retry2, retry3)
                hops.extend(hop_entries)
        print hops
        return hops


    def parse_hop_1host(hop_count, host_fields):
        return {'hop_count': hop_count,
            'domain1': host_fields[0], 'domain2': host_fields[0], 'domain3': host_fields[0],
            'ip1'    : host_fields[1], 'ip2'    : host_fields[1], 'ip3'    : host_fields[1],
            'delay1': host_fields[2], 'delay2': host_fields[4], 'delay3': host_fields[6],
            }

    def parse_hop_3host(hop_count, retry1, retry2, retry3):
        retry1_fields = retry1.split()
        retry2_fields = retry2.split()
        retry3_fields = retry3.split()
        return {'hop_count': hop_count,
            'domain1': retry1_fields[0], 'domain2': retry1_fields[0], 'domain3': retry1_fields[0],
            'ip1'   : retry1_fields[1], 'ip2'   : retry2_fields[1], 'ip3'   : retry3_fields[1],
            'delay1': retry1_fields[2], 'delay2': retry2_fields[2], 'delay3': retry3_fields[2],
            }
    ###


    #insert the tracetoute results into the database
    def insertData(dao, traceroute, hoplist):
        print "Writting to the Traceroute tabele"
        traceroute_id = dao.write_op("traceroute", traceroute)

        print "writing to the Hop table"
        for hop in hoplist:
            print hop
            #hop.traceroute = traceroute_id
            hop['traceroute_id'] = traceroute_id
            dao.write_op("traceroot_hop",hop)


    #parses arguments
    if __name__ == "__main__":
        if platform.system()=="Darwin":
            exit(0)

        #general logging here? unable to connect etc
        config = cheesepi.config.get_config()
        dao = cheesepi.config.get_dao()

        landmarks = cheesepi.config.get_landmarks()
        save_file = cheesepi.config.config_equal("ping_save_file","true")

        print "Landmarks: ",landmarks
        measure(dao, landmarks, save_file)
        dao.close()

