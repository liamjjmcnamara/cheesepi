import sys

import cheesepi.config
import cheesepi.storage.dao

logger = cheesepi.log.get_logger()

try:
    import cheesepi.storage.dao_mongo
except ImportError as exception:
    print("\nProblem importing Mongo python module (or GridFS/bson)...")
    print("Error: " + str(exception))
    print("Possibly try: 'pip install pymongo'")

try:
    import cheesepi.storage.dao_influx08
except ImportError as exception:
    print("\nProblem importing InfluxDB-08 python module...")
    print("Error: " + str(exception))
    print("Possibly try: 'pip install influxdb'")

try:
    import cheesepi.storage.dao_influx09
except ImportError as exception:
    print("\nProblem importing InfluxDB-09 python module...")
    print("Error: " + str(exception))
    print("Possibly try: 'pip install influxdb'")

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
    if cheesepi.config.config_equal('database', "influx09"):
        return cheesepi.storage.dao_influx09.DAO_influx()
    # if cheesepi.config.config_equal('database', "mysql"):
        # return cheesepi.storage.dao_mysql.DAO_mysql()
    if cheesepi.config.config_equal('database', "null"):
        return cheesepi.storage.dao.DAO()

    msg = "Fatal error: 'database' type not set to a valid value in config file, exiting."
    logger.error("Database type: " + str(cheesepi.config.get('database')) + "\n" + msg)
    print(msg)
    sys.exit(1)
