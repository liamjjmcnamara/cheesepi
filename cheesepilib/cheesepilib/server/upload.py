from __future__ import unicode_literals, absolute_import, print_function

import os
import hashlib

from twisted.web import server
from twisted.web.resource import Resource
from twisted.internet import reactor, defer

UPLOAD_PATH = "/tmp/cheesepi/"

class UploadHandler(Resource):

	def __init__(self):
		if not os.path.exists(UPLOAD_PATH):
			os.makedirs(UPLOAD_PATH)

	def render_POST(self, request):

		filename = os.path.join(UPLOAD_PATH,
		                        request.args['filename'][0])

		# Check the hash
		md5_hash = request.args['md5_hash'][0]

		m = hashlib.md5()
		m.update(request.args['fileupload'][0])
		upload_hash = m.hexdigest()
		if md5_hash != upload_hash:
			print("HASH DOES NOT MATCH")
			# Do we care??

		# Write the file
		with open(filename, 'wb') as fd:
				fd.write(request.args['fileupload'][0])

		upload_size = os.stat(filename).st_size

		# Schedule processing of file one second later
		# NOTE: Maybe we'd like to chain together the completion of the
		#       write with the processing using a callback?
		from cheesepilib.server.processing.utils import process_upload
		reactor.callLater(1, process_upload, filename)

		response = b'Received upload of size %d bytes\n' % upload_size
		request.setHeader(b'Content-Length', len(response))

		request.write(response)

		request.finish()

		return server.NOT_DONE_YET
