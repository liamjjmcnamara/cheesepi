#!/bin/bash

# Find containing directory
CLIENT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo $CLIENT_DIR

# Start server
$CLIENT_DIR/tools/influxdb/influxdb -config=$CLIENT_DIR/tools/influxdb/config.toml

