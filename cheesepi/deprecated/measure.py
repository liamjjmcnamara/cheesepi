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

sys.path.append("/usr/local/")
import cheesepi

# all scripts that should be run
actions = ["localMeasure", "pingMeasure", "httpingMeasure", "tracerouteMeasure", "wifiMeasure"]
#"udpMeasure", 'voipMeasure']

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
    #print config

    # Run the measurement suite
    # TODO: convert this from program execution into mathod calling
    for action in actions:
        if cheesepi.config.config_true(action):
            run([config['cheesepi_dir']+"/measure/"+action+".py"])

    # should we upload a dump of collected data to the server?
    if cheesepi.config.should_dump():
        # should do in another process! (will take a while)
        cheesepi.config.log("Info: performing data dump to central server!")
        dumpcall = [config['cheesepi_dir']+"/storage/dump_db.py"]
        run(dumpcall)

    # Update the chesepi distribution?
    if cheesepi.config.should_update():
        cheesepi.config.log("Info: performing distribution update!")
        updatecall = [config['cheesepi_dir']+"/update.py"]
        run(updatecall)

if __name__ == "__main__":
    measure()
