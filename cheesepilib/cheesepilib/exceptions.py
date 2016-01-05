
# The Root Exception
class CheeseLibException(Exception):
    pass


# Peer Exceptions
class CheesePiException(CheeseLibException):
    pass


# Server Exceptions
class CheeseServerException(CheeseLibException):
    pass

class ServerDaoError(CheeseServerException):
    pass

class NoSuchPeer(ServerDaoError):
    pass
