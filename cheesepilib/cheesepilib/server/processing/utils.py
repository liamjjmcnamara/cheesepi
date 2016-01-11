from __future__ import unicode_literals, absolute_import, print_function


import tarfile

# Processing functions, untar, calculating stats etc...
# TODO some kind of logging??
# How do we know where the database is???

def process_upload(uploaded_file):
	from .ResultDataProcessor import ResultDataProcessor

	with ResultDataProcessor(uploaded_file) as data:
		data.process()
		print("Done processing.")

# TODO Maybe this should be baked into ResultDataProcessor
def untar(filename, destination):
	with tarfile.open(filename) as tar:
		tar.extractall(destination)

