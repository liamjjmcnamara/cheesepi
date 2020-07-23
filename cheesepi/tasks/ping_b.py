import time
import os

import cheesepi
from cheesepi.tasks.task import Task

logger = cheesepi.config.get_logger(__name__)

class PingB(Task):

    def __init__(self, dao, spec={}):
        Task.__init__(self, dao, spec)
        self.spec['taskname'] = "pingb"
        if 'landmark' not in self.spec:
            self.spec['landmark'] = "www.sics.se"

    def run(self):
        logger.info("PingBing {} @ {} PID: {}".format(self.spec['landmark'], time.time(), os.getpid()))
        self.measure(self.spec['landmark'])

    def measure(self, landmark):
        #Extract the ethernet MAC address of the PI
        start_time = cheesepi.utils.now()
        output = self.perform(landmark)
        end_time = cheesepi.utils.now()

        logger.debug(output)
        hops = self.parse(output, start_time, end_time)
        self.insertData(self.dao, hops)

    #Execute traceroute function
    def perform(self, target, count=10):
        #traceroute command"
        command = "mtr  --report-wide -c{} {}".format(count, target)
        self.spec['return_code'], output = self.execute(command)
        if self.spec['return_code'] == 0:
            return output
        return None

    def parse(self, data, start_time, end_time):
        self.spec['start'] = start_time
        self.spec['end'] = end_time
        lines = data.split("\n")
        hops = []
        for line in lines[2:-1]:
            fields = line.split()
            hops.append(self.parse_hop(fields))
        #logger.debug("hops: ",hops)
        self.spec['hopcount'] = len(hops)
        self.spec['uploaded'] = 64*8 * self.spec['hopcount']
        return hops

    def parse_hop(self, fields):
        ret = {}
        ret['hop'] = int(fields[0][:-4])
        ret['host'] = fields[1]
        ret['loss'] = float(fields[2][:-1])
        ret['mean'] = float(fields[5])
        ret['min'] = float(fields[6])
        ret['max'] = float(fields[7])
        ret['stdev'] = float(fields[8])
        return ret

    #insert the mtr results into the database
    def insertData(self, dao, hoplist):
        logger.debug("Writting to the PingB table")
        mtr_id = dao.write_op("pingb", self.spec)

        for hop in hoplist:
            logger.debug(hop)
            hop['pingb_id'] = mtr_id
            dao.write_op("pingb_hop", hop)


#parses arguments
if __name__ == "__main__":

    #general logging here? unable to connect etc
    config = cheesepi.config.get_config()
    dao = cheesepi.storage.get_dao()

    spec = {'landmark':'www.sics.se'}
    pingb_task = PingB(dao, spec)
    pingb_task.run()
