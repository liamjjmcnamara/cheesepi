
# Where shall we install CheesePi?
INSTALL_DIR = /usr/local/cheesepi

# Install required OS software
apt-get install mysql

# install python software modules
pip install MySQL-python

# Make main CheesePi directory
mkdir -p $INSTALL_DIR

# Copy cheesepi.conf if it doesnt exist
if [ ! -f $INSTALL_DIR/cheesepi.conf ]; then
	cp $INSTALL_DIR/cheesepi.default.conf $INSTALL_DIR/cheesepi.conf
fi

# Make mysql database and user
$INSTALL_DIR/install/install.sh Measure pi password

