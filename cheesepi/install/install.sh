# Where shall we install CheesePi?
INSTALL_DIR=/usr/local/cheesepi/

# Optionally update apt-get
#sudo apt-get update && sudo apt-get upgrade

# make a local distribution
sudo rsync -avzhe ssh  pi@grayling.sics.se:dist/* $INSTALL_DIR

# Install required OS software
# include ntpdate ?
sudo apt-get update
sudo apt-get install mysql-client mysql-server python-mysqldb
# no root password
sudo apt-get install httping
# Copy cheesepi.conf if it doesnt exist
if [ ! -f $INSTALL_DIR/cheesepi.conf ]; then
	sudo cp $INSTALL_DIR/cheesepi.default.conf $INSTALL_DIR/cheesepi.conf
fi

# Make mysql database and user
# should warn about password prompt requirement
$INSTALL_DIR/install/createDbandUser.sh Measurement measurement MP4MDb

# Intall a crontab entry so that $INSTALL_DIR/measure/measure.py is run
