import time
import os
import logging
import socket
from subprocess import Popen, PIPE

import uptime

import cheesepi as cp
from cheesepi.tasks.task import Task

LOGGER = cp.config.get_logger(__name__)

class Status(Task):

    # construct the process and perform pre-work
    def __init__(self, dao, spec={}):
        Task.__init__(self, dao, spec)
        self.spec['taskname'] = "status"
        self.spec['downloaded'] = 0
        self.spec['uploaded'] = 0

    def run(self):
        LOGGER.info("Status @ %f, PID: %d", time.time(), os.getpid())
        self.measure()

    def measure(self):
        ethmac = cp.utils.get_MAC()
        self.spec['start_time'] = cp.utils.now()
        op_output = self.measure_uptime()
        self.measure_storage()
        self.measure_temperature()
        parsed_output = self.parse_output(op_output, ethmac)
        self.dao.write_op("status", parsed_output)

    def measure_uptime(self):
        execute = "uptime"
        logging.info("Executing: %s", execute)
        LOGGER.debug(execute)
        result = Popen(execute, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        ret = result.stdout.read()
        result.stdout.flush()
        return ret

    def measure_storage(self):
        st = os.statvfs('/')
        self.spec['available_kb'] = (st.f_bavail * st.f_frsize) / 1024
        fs_size = st.f_blocks * st.f_frsize
        fs_used = (st.f_blocks - st.f_bfree) * st.f_frsize
        self.spec['used_storage'] = fs_used / float(fs_size)

    def measure_temperature(self):
        temp = cp.utils.get_temperature()
        if temp is not None:
            self.spec['temperature'] = float(temp/1000.0)

    #read the data from ping and reformat for database entry
    def parse_output(self, data, ethmac):
        self.spec["current_MAC"] = cp.utils.get_MAC()
        self.spec["ethernet_MAC"] = ethmac
        self.spec["source_address"] = cp.utils.get_SA()
        self.spec["local_address"] = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0],
            s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

        fields = data.split()
        self.spec["uptime"] = float(uptime.uptime() / (60*60))
        self.spec["load1"] = float(fields[-3][:-1])
        self.spec["load5"] = float(fields[-2][:-1])
        self.spec["load15"] = float(fields[-1])

        return self.spec

if __name__ == "__main__":
    #general logging here? unable to connect etc
    DAO = cp.storage.get_dao()
    STATUS_TASK = Status(DAO)
    STATUS_TASK.run()
