#!/usr/bin/env python
import subprocess

CHEESEPI_DIR = "/usr/local/cheesepi"


def run(cmd):
    print "Running: "+str(cmd)
    output = subprocess.check_output(cmd)
    return output


run([CHEESEPI_DIR+"/update.sh"])
# if we updated, we should execute the new /measure.py then quit

# Run the measurement suite
run([CHEESEPI_DIR+"/measure/pingMeasurement.py"])
run([CHEESEPI_DIR+"/measure/wifiMeasurement.py"])




