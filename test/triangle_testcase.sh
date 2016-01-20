#!/bin/bash

mkdir -p triangle/peer_{1..3}

P1='beef'
P2='deaf'
P3='feed'

P1_IP='192.168.1.1'
P2_IP='192.168.2.2'
P3_IP='192.168.3.3'

# Generate the test data
python2 mock_ping.py --peerid=$P1 --samplesize=100 --target "{'id':'$P2','ip':'$P2_IP'}" --target "{'id':'$P3','ip':'$P3_IP'}" > triangle/peer_1/ping.json

python2 mock_ping.py --peerid=$P2 --samplesize=100 --target "{'id':'$P1','ip':'$P1_IP'}" --target "{'id':'$P3','ip':'$P3_IP'}" > triangle/peer_2/ping.json

python2 mock_ping.py --peerid=$P3 --samplesize=100 --target "{'id':'$P1','ip':'$P1_IP'}" --target "{'id':'$P2','ip':'$P2_IP'}" > triangle/peer_3/ping.json

cd triangle

cd peer_1 && tar czvf ../${P1}.tgz * && cd ..
cd peer_2 && tar czvf ../${P2}.tgz * && cd ..
cd peer_3 && tar czvf ../${P3}.tgz * && cd ..

P1_HASH=$(md5sum ${P1}.tgz | cut -d ' ' -f 1)
P2_HASH=$(md5sum ${P2}.tgz | cut -d ' ' -f 1)
P3_HASH=$(md5sum ${P3}.tgz | cut -d ' ' -f 1)

curl --form "fileupload=@${P1}.tgz" --form "filename=${P1}.tgz" --form "md5_hash=${P1_HASH}" localhost:18090/upload
curl --form "fileupload=@${P2}.tgz" --form "filename=${P2}.tgz" --form "md5_hash=${P2_HASH}" localhost:18090/upload
curl --form "fileupload=@${P3}.tgz" --form "filename=${P3}.tgz" --form "md5_hash=${P3_HASH}" localhost:18090/upload

rm ${P1}.tgz
rm ${P2}.tgz
rm ${P3}.tgz

echo "Stats of generated data:"
jq "{${P1}: .[0].series[0].distribution_stats}" peer_1/ping.json
jq "{${P2}: .[0].series[0].distribution_stats}" peer_2/ping.json
jq "{${P3}: .[0].series[0].distribution_stats}" peer_3/ping.json
