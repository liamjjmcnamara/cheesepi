import os
import sys
import datetime
from mod_python import apache

NOW = str(datetime.datetime.utcnow().strftime("%s"))
DUMP_DIR="/var/www/html/dump"
if not os.path.exists(DUMP_DIR):
	os.makedirs(DUMP_DIR)

def index(req):
	if not 'file' in req.form or not req.form['file'].filename:
		return "Error: Please upload a file"

	# Record which IP send this file
	ip = req.get_remote_host(apache.REMOTE_NOLOOKUP)
	
	user = auth_user(req.form['ethmac'],"pass?")
	return save_file(req.form['file'], ip, user)

def ensure_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)

def auth_user(mac,path):
	return mac

def save_file(fileitem, ip, user=None):
	# strip leading path from file name to avoid directory traversal attacks
	filename = NOW+".tar.gz"
	if user!=None:
		filename = user+"-"+filename
	#os.path.basename(fileitem.filename)

	# build absolute path to files directory
	host_dir = os.path.join(DUMP_DIR, ip) 
	ensure_dir(host_dir)
	filepath = os.path.join(host_dir, filename)

	fd = open(filepath, 'wb')
	while 1:
        	chunk = fileitem.file.read(100000)
        	if not chunk: break
        	fd.write (chunk)
	message = 'The file "%s" was uploaded successfully from  %s' % (filepath, ip)

	return message
