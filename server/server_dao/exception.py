class ServerDaoError(Exception):
    pass

class NoSuchPeer(ServerDaoError):
    pass
