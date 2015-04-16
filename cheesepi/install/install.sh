# Where shall we install CheesePi?
INSTALL_DIR=/usr/local/cheesepi/

echo "Please enter root pass to enable apt-get software install:"
# Install required OS software
# include ntpdate ?
sudo apt-get update
sudo apt-get install httping python-pip

# add python modules
sudo pip install cherrypy influxdb

# Copy influx config if it doesnt exist
#if [ ! -f $INSTALL_DIR/cheesepi.conf ]; then
#	sudo cp $INSTALL_DIR/cheesepi.default.conf $INSTALL_DIR/cheesepi.conf
#fi


# Intall a crontab entry so that $INSTALL_DIR/measure/measure.py is run
# should avoid duplication...
echo -e "#cheesepi measurement\n*/5 * * * * python $INSTALL_DIR/measure/measure.py &" >> /etc/crontab

# Try to run it
$INSTALL_DIR/measure/measure.py 
