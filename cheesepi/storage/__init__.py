import dao

try:
	import dao_mongo
except ImportError:
	print "Missing Mongo python module (and GridFS and bson), use 'pip install pymongo'"

try:
	import dao_influx
except ImportError:
	print "Missing InfluxDB python module, use 'pip install influxdb'"

try:
	import dao_mysql
except ImportError:
	print "Missing MySQL python module, use 'pip install MySQL-python'"

