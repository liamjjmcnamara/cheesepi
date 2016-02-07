
# The Root Exception
class CheesePiLibException(Exception):
    pass


# Peer Exceptions
class CheesePiException(CheesePiLibException):
    pass


# Server Exceptions
class CheesePiServerException(CheesePiLibException):
    pass

class ServerDaoError(CheesePiServerException):
    pass

class NoSuchPeer(ServerDaoError):
    pass

class UnsupportedResultType(CheesePiServerException):
    pass

class UnsupportedEntityType(CheesePiServerException):
    pass
