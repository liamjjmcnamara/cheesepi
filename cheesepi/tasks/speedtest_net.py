#!/usr/bin/env python3

import os
import re
import sys
import time
import speedtest

import cheesepi
from cheesepi.tasks.task import Task

logger = cheesepi.config.get_logger(__name__)

class SpeedtestNet(Task):
    # construct the process and perform pre-work
    def __init__(self, dao, parameters):
        Task.__init__(self, dao, parameters)

    # actually perform the measurements, no arguments required
    def run(self):
        logger.info("Speedtest: @ %f, PID: %d", time.time(), os.getpid())
        self.measure()

    #main measure funtion
    def measure(self):
        start_time = cheesepi.utils.now()
        op_output = self.perform()
        end_time = cheesepi.utils.now()
        logger.debug(op_output)
        if op_output is not None:
            self.parse_output(op_output.decode("utf-8"), landmark, start_time, end_time, ping_count)
        self.dao.write_op("speedtest", self.spec)

    #ping function
    def perform(self, servers=[]):
        threads = None
        # If you want to use a single threaded test
        # threads = 1

        s = Speedtest()
        s.get_servers(servers)
        s.get_best_server()
        s.download(threads=threads)
        s.upload(threads=threads)
        s.results.share()

        results_dict = s.results.dict()
        return None

if __name__ == "__main__":
    # general logging here? unable to connect etc
    config = cheesepi.config.get_config()
    dao = cheesepi.storage.get_dao()

    speedtest_task = SpeedtestNet(dao, {})
    speedtest_task.run()
