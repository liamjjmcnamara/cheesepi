echo "Starting servers..."
# following should end up being /usr/local/cheesepi
INSTALL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

# Influx needs to spool up
INFLUX_DIR=$INSTALL_DIR/client/tools/influxdb
INFLUX_CMD="$INFLUX_DIR/influxdb -config=$INFLUX_DIR/config.toml"
echo -e "Running: $INFLUX_CMD"
nohup sudo $INFLUX_CMD >&/dev/null &

# and the webserver serving a grafana dashboard
echo "Running: $INSTALL_DIR/client/webserver/webserver.py"
sudo $INSTALL_DIR/webserver/webserver.py &

echo "Started servers..."

sleep 5

exit 0
