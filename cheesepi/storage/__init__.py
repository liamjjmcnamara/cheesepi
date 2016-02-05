import dao

try:
	import dao_mongo
except ImportError as e:
	print "Missing Mongo python module (and GridFS and bson), use 'pip install pymongo'"
	print str(e)

try:
	import dao_influx08
except ImportError as e:
	print "Missing InfluxDB python module, use 'pip install influxdb'"
	print str(e)

try:
	import dao_influx09
except ImportError as e:
	print "Missing InfluxDB python module, use 'pip install influxdb'"
	print str(e)

#try:
#	import dao_mysql
#except ImportError as e:
#	print "Missing MySQL python module, use 'pip install MySQL-python'"
#	print str(e)

