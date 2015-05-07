
# following should end up being /usr/local/cheesepi
INSTALL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

# Influx needs to spool up
INFLUX_DIR=$INSTALL_DIR/tools/influxdb
INFLUX_CMD="$INFLUX_DIR/influxdb -config=$INFLUX_DIR/config.toml"
echo $INFLUX_CMD
nohup $INFLUX_CMD &

# and the webserver serving a grafana dashboard
echo "$INSTALL_DIR/webserver/webserver.py"
$INSTALL_DIR/webserver/webserver.py &
sleep 5

