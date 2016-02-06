#!/bin/bash

mkdir -p triangle/peer_{1..3}

P1='54a7969d-8436-49a3-a242-937dcf7c2d36'
P2='14db8b89-cbf7-431a-90f0-b6ccc6bc7afc'
P3='4f719cf1-d23f-4c6c-a6d8-c52eaf77a53f'

P1_IP='192.168.1.1'
P2_IP='192.168.2.2'
P3_IP='192.168.3.3'

P1_P2_ARGS="'shape':3"
P1_P3_ARGS=""
P2_P1_ARGS="'loc':15"
P2_P3_ARGS=""
P3_P1_ARGS="'scale':5"
P3_P2_ARGS="'lossrate':0.5"

# Generate the test data
python2 mock_ping.py --peerid=$P1 --samplesize=100 --target "{'id':'$P2','ip':'$P2_IP',$P1_P2_ARGS}" --target "{'id':'$P3','ip':'$P3_IP',$P1_P3_ARGS}" > triangle/peer_1/ping.json

python2 mock_ping.py --peerid=$P2 --samplesize=100 --target "{'id':'$P1','ip':'$P1_IP',$P2_P1_ARGS}" --target "{'id':'$P3','ip':'$P3_IP',$P2_P3_ARGS}" > triangle/peer_2/ping.json

python2 mock_ping.py --peerid=$P3 --samplesize=100 --target "{'id':'$P1','ip':'$P1_IP',$P3_P1_ARGS}" --target "{'id':'$P2','ip':'$P2_IP',$P3_P2_ARGS}" > triangle/peer_3/ping.json

cd triangle

cd peer_1 && tar czvf ../${P1}.tgz * && cd ..
cd peer_2 && tar czvf ../${P2}.tgz * && cd ..
cd peer_3 && tar czvf ../${P3}.tgz * && cd ..

P1_HASH=$(md5sum ${P1}.tgz | cut -d ' ' -f 1)
P2_HASH=$(md5sum ${P2}.tgz | cut -d ' ' -f 1)
P3_HASH=$(md5sum ${P3}.tgz | cut -d ' ' -f 1)

curl --form "file=@${P1}.tgz" --form "filename=${P1}.tgz" --form "md5_hash=${P1_HASH}" localhost:18090/upload
curl --form "file=@${P2}.tgz" --form "filename=${P2}.tgz" --form "md5_hash=${P2_HASH}" localhost:18090/upload
curl --form "file=@${P3}.tgz" --form "filename=${P3}.tgz" --form "md5_hash=${P3_HASH}" localhost:18090/upload

rm ${P1}.tgz
rm ${P2}.tgz
rm ${P3}.tgz

echo "Stats of generated data:"
jq "{\"${P1}\": .[0].series[0].distribution_stats}" peer_1/ping.json
jq "{\"${P2}\": .[0].series[0].distribution_stats}" peer_2/ping.json
jq "{\"${P3}\": .[0].series[0].distribution_stats}" peer_3/ping.json
