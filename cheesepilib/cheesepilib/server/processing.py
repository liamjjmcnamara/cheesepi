from __future__ import unicode_literals, absolute_import, print_function


import tarfile
import hashlib
import os

# Processing functions, untar, calculating stats etc...
# TODO some kind of logging??

def process_upload(uploaded_file):
	hasher = hashlib.md5()
	with open(uploaded_file) as fd:
		hasher.update(fd.read())
	md5_hash = hasher.hexdigest()
	print(md5_hash)

	path = os.path.dirname(uploaded_file)
	destination = os.path.join(path, md5_hash)

	untar(uploaded_file, destination)

def untar(filename, destination):
	with tarfile.open(filename) as tar:
		tar.extractall(destination)
