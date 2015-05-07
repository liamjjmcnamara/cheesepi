# Where shall we install CheesePi?
# This can be changed but will currently break the Influx and Grafana config files
# following should end up being /usr/local/cheesepi
INSTALL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

# Quit if any command fails...
set -e

# Discover local IP address
# To be used in the grafana configuration (so it knows where the Influx DB is)
LOCAL_IP=`hostname -I |head -n1| tr -d '[[:space:]]'`

# Copy Influx config if it doesnt exist
echo "Starting InfluxDB..."
if [ ! -f $INSTALL_DIR/tools/influxdb/config.toml ]; then
	cp $INSTALL_DIR/tools/influxdb/config.sample.toml $INSTALL_DIR/tools/influxdb/config.toml
fi
# Influx needs to spool up
INFLUX_DIR=$INSTALL_DIR/tools/influxdb
INFLUX_CMD="$INFLUX_DIR/influxdb -config=$INFLUX_DIR/config.toml"
echo $INFLUX_CMD
nohup $INFLUX_CMD &
sleep 5


# # Install required OS software
echo "Enter root pass to enable apt-get software install if prompted..."
# Ensure we have uptodate package definition
sudo apt-get update

# Optional software for speed improvements (through a binary module)
sudo apt-get install build-essential python-dev

sudo apt-get install httping python-pip python-mysqldb
# include ntpdate ?
# add python modules
sudo pip install cherrypy influxdb pymongo


## Copy the Grafana config file, adding the local IP address
if [ ! -f $INSTALL_DIR/webserver/dashboard/config.js ]; then
	sudo cat $INSTALL_DIR/webserver/dashboard/config.sample.js| sed "s/my_influxdb_server/$LOCAL_IP/" >$INSTALL_DIR/webserver/dashboard/config.js
fi
# and the webserver serving a grafana dashboard
echo "$INSTALL_DIR/webserver/webserver.py"
$INSTALL_DIR/webserver/webserver.py &
sleep 5


## Have both Influx and webserver start on boot
#sudo echo $INFLUX_CMD >> /etc/rc.local
#echo $INFLUX_CMD | sudo tee --append /etc/rc.local
if ! grep --quiet influxdb /etc/inittab; then
	echo -e "\nC1:2345:boot:$INFLUX_CMD" | sudo tee --append /etc/inittab
	echo "W1:2345:boot:$INSTALL_DIR/webserver/webserver.py" | sudo tee --append /etc/inittab
fi


## Install a crontab entry so that $INSTALL_DIR/measure/measure.py is run
if ! grep --quiet measure.py /etc/crontab; then
	echo -e "\n*/5 *   * * *   root    /usr/local/cheesepi/measure/measure.py" | sudo tee --append /etc/crontab
fi


## Create Influx 'cheesepi' and 'grafana' databases
# Very quick and dirty solution
echo "Waiting for Influx to definitely be started..."
sleep 20
$INSTALL_DIR/install/installDB.sh


## Inform user of dashboard website
echo -e "\nInstalled!\nVisit $LOCAL_IP:8080/dashboard to see your dashboard!\n"

