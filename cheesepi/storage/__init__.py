import cheesepi.storage.dao

try:
	import cheesepi.storage.dao_mongo
except ImportError as e:
	print("\nProblem importing Mongo python module (or GridFS/bson)...")
	print("Error: " + str(e))
	print("Possibly try: 'pip install pymongo'")

try:
	import cheesepi.storage.dao_influx08
except ImportError as e:
	print("\nProblem importing InfluxDB-08 python module...")
	print("Error: " + str(e))
	print("Possibly try: 'pip install influxdb'")

try:
	import cheesepi.storage.dao_influx09
except ImportError as e:
	print("\nProblem importing InfluxDB-09 python module...")
	print("Error: " + str(e))
	print("Possibly try: 'pip install influxdb'")

#try:
#	import dao_mysql
#except ImportError as e:
#	print("Problem importing MySQL python module, use 'pip install MySQL-python'"
#	print(str(e)

