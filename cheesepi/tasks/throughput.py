#!/usr/bin/env python

import os
import time

import speedtest

import cheesepi
from cheesepi.tasks.task import Task

LOGGER = cheesepi.config.get_logger(__name__)

class Throughput(Task):

    # construct the process and perform pre-work
    def __init__(self, dao, spec):
        super().__init__()
        Task.__init__(self, dao, spec)
        self.spec['taskname'] = "throughput"

    def run(self):
        LOGGER.info("Speedtest throughput: @ %f, PID: %d", time.time(), os.getpid())
        self.measure()

    def measure(self):
        threads = None
        servers = []
        self.spec['start_time'] = cheesepi.utils.now()
        st = speedtest.Speedtest()
        st.get_servers(servers)
        st.get_best_server()
        st.download(threads=threads)
        st.upload(threads=threads)
        st.results.share()
        self.spec['end_time'] = cheesepi.utils.now()

        op_output = st.results.dict()
        LOGGER.debug(op_output)

        parsed_output = self.parse_output(op_output)
        self.dao.write_op(self.spec['taskname'], parsed_output)

    #read the data and reformat for database entry
    def parse_output(self, data):
        self.spec['ping'] = data['ping']
        self.spec['server'] = data['server']['url']
        self.spec['download_speed'] = data['download']
        self.spec['upload_speed'] = data['upload']
        self.spec['bytes_received'] = data['bytes_received']
        self.spec['bytes_sent'] = data['bytes_sent']
        return self.spec

if __name__ == "__main__":
    DAO = cheesepi.storage.get_dao()
    SPEC = {}
    TASK = Throughput(DAO, SPEC)
    TASK.run()
