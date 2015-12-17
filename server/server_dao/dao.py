class DAO():

    # TODO: define parameters and return values explicitly with comments

    def __init__(self):
        pass

    def close(self):
        pass

    def peer_beacon(self, peer_id, host, last_seen):
        pass

    def active_peers(self, since):
        pass

    def register_peer(self, peer_id, host):
        pass

    def find_peer(self):
        pass

    def get_peers(self):
        pass

    def get_random_peer(self):
        pass

    def write_result(self, peer_id, result):
        pass

    def purge_results(self, peer_id):
        pass

    def purge_results_older_than(self, peer_id, timestamp):
        pass

    def write_task(self, peer_id, task):
        pass

    def _return_status(self, boolean):
        if boolean:
            return {'status':'success'}
        else:
            return {'status':'failure'}
