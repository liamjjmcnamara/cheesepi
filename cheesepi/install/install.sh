# Where shall we install CheesePi?
INSTALL_DIR=/usr/local/cheesepi

echo "Enter root pass to enable apt-get software install if prompted..."
# Install required OS software
#sudo apt-get update
sudo apt-get install httping python-pip python-mysqldb
# include ntpdate ?

# add python modules
sudo pip install cherrypy influxdb pymongo


# Copy Influx config if it doesnt exist
if [ ! -f $INSTALL_DIR/tools/influxdb/config.toml ]; then
	sudo cp $INSTALL_DIR/tools/influxdb/config.sample.toml $INSTALL_DIR/tools/influxdb/config.toml
fi

# Start Influx database server
INFLUX_DIR=$INSTALL_DIR/tools/influxdb
INFLUX_CMD="$INFLUX_DIR/influxdb -config=$INFLUX_DIR/config.toml"
$INFLUX_CMD &
# and the webserver serving a grafana dashboard
$INSTALL_DIR/webserver/webserver.py &

# ..and have both start on boot
#sudo echo $INFLUX_CMD >> /etc/rc.local
#echo $INFLUX_CMD | sudo tee --append /etc/rc.local
if ! grep --quiet influxdb /etc/inittab; then
	echo -e "\nC1:2345:boot:$INFLUX_CMD" | sudo tee --append /etc/inittab
	echo "W1:2345:boot:$INSTALL_DIR/webserver/webserver.py" | sudo tee --append /etc/inittab
fi

# Create Influx 'cheesepi' databases
#$INSTALL_DIR/install/makeInfluxDB.py
# Very quick and dirty solution
curl -s "http://localhost:8086/db?u=root&p=root" -d "{\"name\": \"cheesepi\"}"
curl -s "http://localhost:8086/db?u=root&p=root" -d "{\"name\": \"grafana\"}"


# Intall a crontab entry so that $INSTALL_DIR/measure/measure.py is run
if ! grep --quiet measure.py /etc/crontab; then
	echo -e "\n*/5 * * * * python $INSTALL_DIR/measure/measure.py" | sudo tee --append /etc/crontab
fi

# Try to run the measure script
#$INSTALL_DIR/measure/measure.py 

# Ensure the "cheesepi" module can be imported
echo -e "\nAdd '/usr/local' to your python search path, append the following to ~/.profile\nexport PYTHONPATH=/usr/local\n"
