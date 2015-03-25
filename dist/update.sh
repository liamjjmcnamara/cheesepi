#!/bin/bash

# pull the latest files from the server
sudo rsync -avzhe ssh  pi@grayling.sics.se:cheesepi/dist/* /usr/local/cheesepi/

# Perform git clone from a read-only user account with no git repos history
#git clone --depth=1 https://bitbucket.org/IanRobinMarsh/cheesepi.git
