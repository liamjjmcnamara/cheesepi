from __future__ import unicode_literals, absolute_import, print_function

import heapq

from cheesepilib.server.storage.mongo import MongoDAO
from .Scheduler import Scheduler

class PingScheduler(Scheduler):

    def __init__(self, peer_id):
        self.dao = MongoDAO('localhost', 27017)
        self._peer_id = peer_id

    def get_schedule(self, num=1):
        schedule = []

        stats = self.dao.get_all_stats(self._peer_id)

        from pprint import pformat

        #print(pformat(stats.toDict()))

        priority_sorted_targets = []

        for s in stats:
            #print(pformat(s.toDict()))
            delay_variance = s._delay._variance
            target_id = s.get_target().get_id()
            #print(target_id)
            #print(delay_variance)
            heapq.heappush(priority_sorted_targets, (-delay_variance, target_id))

        #print(priority_sorted_targets)

        for i in range(0, num):
            target = heapq.heappop(priority_sorted_targets)
            schedule.append(target[1])

        return schedule


if __name__ == "__main__":
    import argparse
    import cheesepilib.server.utils as utils

    utils.init_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default=None)

    args = parser.parse_args()

    ps = PingScheduler(args.id)

    schedule = ps.get_schedule()
    print(schedule)
