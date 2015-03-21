#!/bin/bash

# pull the latest files from the server
sudo rsync -avzhe ssh  pi@grayling.sics.se:cheesepi /usr/local/
