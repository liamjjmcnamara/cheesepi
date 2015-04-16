# Where shall we install CheesePi?
INSTALL_DIR=/usr/local/cheesepi

echo "Enter root pass to enable apt-get software install if prompted..."
# Install required OS software
#sudo apt-get update
sudo apt-get install httping python-pip
# include ntpdate ?

# add python modules
pip install cherrypy influxdb


# Copy Influx config if it doesnt exist
if [ ! -f $INSTALL_DIR/tools/influxdb/config.toml ]; then
	sudo cp $INSTALL_DIR/tools/influxdb/config.sample.toml $INSTALL_DIR/tools/influxdb/config.toml
fi

# Start Influx database server
INFLUX_DIR=$INSTALL_DIR/tools/influxdb
INFLUX_CMD="$INFLUX_DIR/influxdb -config=$INFLUX_DIR/config.toml"
$INFLUX_CMD

# ..and have it start on boot
#sudo echo $INFLUX_CMD >> /etc/rc.local
#echo $INFLUX_CMD | sudo tee --append /etc/rc.local
#echo "C1:2345:boot:$INFLUX_CMD" >> /etc/inittab

# Create 'cheesepi' database
#$INSTALL_DIR/install/makeDB.py


# Intall a crontab entry so that $INSTALL_DIR/measure/measure.py is run
# should avoid duplication...
#sudo echo "*/5 * * * * python $INSTALL_DIR/measure/measure.py" >> /etc/crontab
echo "*/5 * * * * python $INSTALL_DIR/measure/measure.py" | sudo tee --append /etc/crontab

# Try to run the measure script
$INSTALL_DIR/measure/measure.py 
