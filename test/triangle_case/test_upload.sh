#!/bin/bash

cd triangle_peer_1 && tar czvf ../beef.tgz * && cd ..
cd triangle_peer_2 && tar czvf ../deed.tgz * && cd ..
cd triangle_peer_3 && tar czvf ../feed.tgz * && cd ..

BEEF_HASH=$(md5sum beef.tgz | cut -d ' ' -f 1)
DEED_HASH=$(md5sum deed.tgz | cut -d ' ' -f 1)
FEED_HASH=$(md5sum feed.tgz | cut -d ' ' -f 1)

curl --form "fileupload=@beef.tgz" --form "filename=beef.tgz" --form "md5_hash=${BEEF_HASH}" localhost:18090/upload
curl --form "fileupload=@deed.tgz" --form "filename=deed.tgz" --form "md5_hash=${DEED_HASH}" localhost:18090/upload
curl --form "fileupload=@feed.tgz" --form "filename=feed.tgz" --form "md5_hash=${FEED_HASH}" localhost:18090/upload

rm beef.tgz
rm deed.tgz
rm feed.tgz
