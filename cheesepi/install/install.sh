# Where shall we install CheesePi?
# This can be changed but will currently break the Influx and Grafana config files
# following should end up being /usr/local/cheesepi
INSTALL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

# # Install required OS software
echo -e "\nEnter root pass to enable apt-get software install if prompted."
echo "Updating apt-get sources:"
# Ensure we have uptodate package definition
sudo apt-get update

# Quit if any command fails...
set -e


echo -e "\nInstalling required software:"
# latter two only for faster binary python modules
sudo apt-get install httping python-pip python-mysqldb build-essential python-dev
# add python modules
sudo pip install cherrypy influxdb pymongo


# Discover local IP address
# To be used in the grafana configuration (so it knows where the Influx DB is)
LOCAL_IP=`hostname -I |head -n1| tr -d '[[:space:]]'`

# Copy Influx config if it doesnt exist
if [ ! -f $INSTALL_DIR/tools/influxdb/config.toml ]; then
	cp $INSTALL_DIR/tools/influxdb/config.sample.toml $INSTALL_DIR/tools/influxdb/config.toml
fi



## Copy the Grafana config file, adding the local IP address
if [ ! -f $INSTALL_DIR/webserver/dashboard/config.js ]; then
	sudo cat $INSTALL_DIR/webserver/dashboard/config.sample.js| sed "s/my_influxdb_server/$LOCAL_IP/" | sudo tee $INSTALL_DIR/webserver/dashboard/config.js > /dev/null
fi

# disable exit on error
set +e

# start the influx and web servers
$INSTALL_DIR/install/start_servers.sh
sleep 20


## Have both Influx and webserver start on boot
#sudo echo $INFLUX_CMD >> /etc/rc.local
#echo $INFLUX_CMD | sudo tee --append /etc/rc.local
if ! grep --quiet influxdb /etc/inittab; then
	echo -e "\nC1:2345:boot:$INFLUX_CMD" | sudo tee --append /etc/inittab > /dev/null
	echo "W1:2345:boot:$INSTALL_DIR/webserver/webserver.py" | sudo tee --append /etc/inittab > /dev/null
fi


## Install a crontab entry so that $INSTALL_DIR/measure/measure.py is run
if ! grep --quiet measure.py /etc/crontab; then
	echo -e "\n*/5 *   * * *   root    /usr/local/cheesepi/measure/measure.py" | sudo tee --append /etc/crontab > /dev/null
fi



## Inform user of dashboard website
echo -e "\n\nInstalled!\nVisit http://$LOCAL_IP:8080/dashboard to see your dashboard!\n"

echo "If the servers (influx/webserver.py) have not started, run the the $INSTALL_DIR/install/start_servers.sh script"

sleep 5
