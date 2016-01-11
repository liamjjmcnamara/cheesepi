#!/bin/bash
curl --form "fileupload=@upload.tgz" --form "filename=upload.tgz" --form "md5_hash=ea8a5f0664f3419d8747c635af2f0066" localhost:18090/upload
