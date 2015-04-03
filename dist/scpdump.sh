#!/bin/sh

echo ""
eth=`/sbin/ifconfig eth0 | egrep -o '([[:xdigit:]]{2}[:]){5}[[:xdigit:]]{2}'`
now=$(date +"%m-%d-%Y-%H:%M:%S")
echo $eth
file="/home/pi/$eth$now.sql"
echo $now
echo $file
dbuser='urban'
dbpassword='basketphone'
dbname='sicspi'
tablename='ping'

wherecond='--where'
condition="ts BETWEEN timestamp(DATE_SUB(NOW(), INTERVAL 24 hour)) AND timestamp(NOW())"
mysqldump -u$dbuser -p$dbpassword $dbname $tablename $wherecond "$condition" > $file

host='pi@grayling.sics.se'
directory='/home/pi/Buffer'
scp $file $host:$directory
retvalue=$?

if [ $retvalue = 0 ]; then
        echo "Done"
else
        echo "Could not send the dump"
        echo "Return value: $retvalue"
fi

