#!/usr/bin/env python
""" Copyright (c) 2015, Swedish Institute of Computer Science
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
      * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
      * Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.
      * Neither the name of The Swedish Institute of Computer Science nor the
        names of its contributors may be used to endorse or promote products
        derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE SWEDISH INSTITUTE OF COMPUTER SCIENCE BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Authors: ljjm@sics.se
Testers:
"""
import sys
import subprocess

# try to import cheesepi, i.e. it's on PYTHONPATH
try:
    import cheesepi
except:
    # try default location
    sys.path.append("/usr/local/")
    import cheesepi

# all scripts that should be run
actions = ["wifiMeasure", "udpMeasure", 'voipMeasure']

def run(cmd):
    """Execute the given command, and log failures"""
    print "Running: "+str(cmd)
    output=""
    try:
        output = subprocess.check_output(cmd)
    except Exception as e:
        cheesepi.config.log("Running command %s failed: %s" % (str(cmd),str(e)))
    return output


# failure of any part of this, should log the error!
def measure(config=None):
    global actions
    if config==None:
        config=cheesepi.config.get_config()
    print config
    # Update the distribution
    if cheesepi.config.isTrue(config, 'auto_update'):
        cheesepi.config.log("Info: performing distribution update!")
        updatecall = [config['cheesepi_dir']+"/update.sh"]
        run(updatecall)
        # if we updated, we should execute the new /measure.py then quit

    pingMeasure(config)

    # Run the measurement suite
    for action in actions:
        if cheesepi.config.isTrue(config, action):
            run([config['cheesepi_dir']+"/measure/"+action+".py"])


def pingMeasure(config):
    if not cheesepi.config.isTrue(config, 'pingMeasure'):
        return
    if 'landmarks' not in config:
        cheesepi.config.log("Error: no landmarks defined!")
        return

    targets = config['landmarks'].split()
    pingcall = [config['cheesepi_dir']+"/measure/pingMeasure.py"]
    for target in targets:
        pingcall.append(target)
    run(pingcall)


if __name__ == "__main__":
    measure()
