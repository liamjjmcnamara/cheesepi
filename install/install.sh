#!/bin/bash

# Where shall we install CheesePi?
# This can be changed but should probably be /usr/local/cheesepi
# Though could be ~/cheesepi or somewhere else through the -d parameter
INSTALL_DIR=/usr/local/cheesepi

usage() { 
	echo "Usage: $0 [-d INSTALL_DIR]"; 
	echo -e "\tINSTALL_DIR is the directory CheesePi will be installed (default: $INSTALL_DIR)"
	exit 1; 
}

# Detect command line parameters
while getopts ":d:" o; do
	case "${o}" in
		d)
			INSTALL_DIR=${OPTARG}
			;;
		*)
			usage
			;;
	esac
done

exit

# Ensure we are not root
if [ $EUID -eq 0 ]; then
	echo "Error: do not run this script as root"
	exit 1
fi





# Where is the cheesepi source loacated
SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"


# # Install required OS software
echo "Updating apt-get sources..."
echo -e "\nEnter root pass if prompted to enable apt-get software install."
# Ensure we have uptodate package definition
#sudo apt-get update
echo "Updated apt-get sources."

# Quit if any command fails...
set -e


echo -e "\nInstalling required software..."
# latter two only for faster binary python modules
#sudo apt-get install httping python-pip python-mysqldb build-essential python-dev iperf libav-tools
# add python modules
#sudo pip install cherrypy influxdb pymongo future
echo -e "Installed required software.\n"


echo "Installing cheesepi from '$SOURCE_DIR' to '$INSTALL_DIR'"
sudo mkdir -p $INSTALL_DIR
sudo cp -rp $SOURCE_DIR/cheesepilib $INSTALL_DIR/cheesepilib
sudo cp -rp $SOURCE_DIR/client $INSTALL_DIR/client
sudo cp -rp $SOURCE_DIR/install $INSTALL_DIR/install

# Install cheesepi python library
echo "Install CheesePi python module in $INSTALL_DIR/cheesepilib"
sudo pip install -e $INSTALL_DIR/cheesepilib

# Discover local IP address
# To be used in the grafana configuration (so it knows where the Influx DB is)
LOCAL_IP=`hostname -I |head -n1| tr -d '[[:space:]]'`
# Should check this worked, and make alternate OSX version

# Copy Influx config if it doesnt exist
DB_DIR=$INSTALL_DIR/client/tools/influxdb
if [ ! -f $DB_DIR/config.toml ]; then
	sudo cat $DB_DIR/config.sample.toml| sed "s#INFLUX_DIR#$DB_DIR#" | sudo tee $DB_DIR/config.toml > /dev/null
	echo "Copied Influx config file: $DB_DIR/config.toml"
else
	echo "Warning: Influx config file '$DB_DIR/config.toml' already exists, not copying."
fi



## Copy the Grafana config file, adding the local IP address
DASHBOARD_DIR=$INSTALL_DIR/client/webserver/dashboard
if [ ! -f $DASHBOARD_DIR/config.js ]; then
	sudo cat $DASHBOARD_DIR/config.sample.js| sed "s/INFLUXDB_IP/$LOCAL_IP/" | sudo tee $DASHBOARD_DIR/config.js > /dev/null
	echo "Copied dashboard config file: config.toml"
else
	echo "Warning: Dashboard config file already exists, not copying."
fi

# disable exit on error
set +e

# start the influx and web servers now
$INSTALL_DIR/install/start_servers.sh
sleep 20


$INSTALL_DIR/install/make_influx_DBs.sh

## Inform user of dashboard website
echo -e "\n\nInstalled! This script has just done the following steps:"
echo -e " -Updated apt-get package lists\n -Installed required software"
echo -e " -Copied config files for the Influx server and the CheesePi dashboard webserver (webserver.py)"
echo -e " -Set these servers to start automatically on boot (inittab) and right now"
echo -e "\nVisit http://$LOCAL_IP:8080/dashboard to see your dashboard!\n"


sleep 5
INFLUX_CMD=$INFLUX_DIR/influxdb
if [ ! -f /etc/inittab ]; then
	echo "This system does not have /etc/inittab, server inittab auto-start will not be installed."
else
	## Have both Influx and webserver start on boot
	if grep --quiet influxdb /etc/inittab; then
		echo "Seems Influx is already configured to start at boot."
	else
		echo "\nC1:2345:boot:$INFLUX_CMD" | sudo tee --append /etc/inittab > /dev/null
		echo "W1:2345:boot:$INSTALL_DIR/webserver/webserver.py" | sudo tee --append /etc/inittab > /dev/null
		echo "Set InfluxDB and dashboard webserver to start at boot."
	fi
fi

echo "If the servers (influx/webserver.py) have not started, run the the $INSTALL_DIR/install/start_servers.sh script"
