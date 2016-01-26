echo "Starting servers..."
# following should end up being /usr/local/cheesepi
INSTALL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

# Influx needs to spool up
INFLUX_DIR=$INSTALL_DIR/bin/tools/influxdb
INFLUX_CMD="$INFLUX_DIR/influxdb -config=$INFLUX_DIR/config.toml"
echo -e "Running: $INFLUX_CMD"
nohup $INFLUX_CMD >&/dev/null &

# and the webserver serving a grafana dashboard
DASH_CMD=$INSTALL_DIR/bin/webserver/webserver.py
echo "Running: $DASH_CMD"

# Note: sometimes seems to want sudo access...
$DASH_CMD &

echo -e "Started servers.\n"

exit 0
