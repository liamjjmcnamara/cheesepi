#!/usr/bin/env python
import subprocess
import os
import sys

CHEESEPI_DIR = "/usr/local/cheesepi"


def run(cmd):
    output = subprocess.check_output(cmd)


run([CHEESEPI_DIR+"/measure/pingMeasurement.py"])




