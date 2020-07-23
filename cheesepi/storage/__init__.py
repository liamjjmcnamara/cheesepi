import sys

import cheesepi.config
from . import dao
from . import dao_influx

logger = cheesepi.log.get_logger()

try:
    import cheesepi.storage.dao_influx
except ImportError as exception:
    print("\nProblem importing InfluxDB python module...")
    print("Error: " + str(exception))
    print("Possibly try: 'pip3 install influxdb'")

try:
    import cheesepi.storage.dao_mongo
except ImportError as exception:
    print("\nProblem importing Mongo python module (or GridFS/bson)...")
    print("Error: " + str(exception))
    print("Possibly try: 'pip3 install pymongo'")

#try:
#    import dao_mysql
#except ImportError as e:
#    print("Problem importing MySQL python module, use 'pip install MySQL-python'"
#    print(str(e)

def get_dao():
    if cheesepi.config.config_equal('database', "mongo"):
        return cheesepi.storage.dao_mongo.DAO_mongo()
    # if cheesepi.config.config_equal('database', "influx08"):
        # return cheesepi.storage.dao_influx08.DAO_influx()
    if cheesepi.config.config_equal('database', "influx"):
        return dao_influx.DAO_influx()
    # if cheesepi.config.config_equal('database', "mysql"):
        # return cheesepi.storage.dao_mysql.DAO_mysql()
    if cheesepi.config.config_equal('database', "null"):
        return cheesepi.storage.dao.DAO()

    msg = "Fatal error: 'database' type not set to a valid value in config file, exiting."
    logger.error("Database type: " + str(cheesepi.config.get('database')) + "\n" + msg)
    print(msg)
    sys.exit(1)
