#!/usr/bin/env python

import time
import os

# slightly modified to return collected data
# It also requires a newer argparse, 1.4 works
# https://pypi.python.org/pypi/speedtest-cli/

import cheesepi as cp
from cheesepi.tasks.task import Task
import cheesepi.tasks.speedtest

logger = cp.config.get_logger(__name__)


class Throughput(Task):

    # construct the process and perform pre-work
    def __init__(self, dao, spec):
        Task.__init__(self, dao, spec)
        self.spec['taskname'] = "throughput"

    # actually perform the measurements, no arguments required
    def run(self):
        logger.info("Speedtest throughput: @ {}, PID: {}".format((time.time(), os.getpid())))
        self.measure()

    # measure and record funtion
    def measure(self):
        op_output=""
        self.spec['start_time'] = cp.utils.now()
        try:
            op_output = speedtest.speedtest()
            print(op_output)
        except Exception as e:
            logger.error("speedtest_cli failed: {}".format(e))
            return
        self.spec['end_time']= cp.utils.now()
        logger.debug(op_output)

        parsed_output = self.parse_output(op_output)
        self.dao.write_op(self.spec['taskname'], parsed_output)

    #read the data and reformat for database entry
    def parse_output(self, data):
        self.spec['download_speed'] = data['download']
        self.spec['upload_speed']   = data['upload']
        self.spec['serverid'] = data['serverid']
        self.spec['ping']     = data['ping']
        # how much data was transferred? calcualted from speedtest.py
        self.spec['downloaded'] = 19100
        self.spec['uploaded']   = 750000
        return self.spec

if __name__ == "__main__":
    #general logging here? unable to connect etc
    dao = cp.config.get_dao()

    spec={}
    throughput_task = Throughput(dao, spec)
    throughput_task.run()
