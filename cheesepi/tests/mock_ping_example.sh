#!/bin/bash
python2 mock_ping.py --peerid='beef' --seed=1 --samplesize=100 --target "{'id':'deaf','ip':'192.168.2.2'}" --target "{'id':'feed','ip':'192.168.3.3'}"
