import os
import re
import datetime
from mod_python import apache


NOW = str(datetime.datetime.utcnow().strftime("%s"))
DUMP_DIR="/var/www/html/dump"
if not os.path.exists(DUMP_DIR):
	os.makedirs(DUMP_DIR)

def index(req):
	if not 'file' in req.form or not req.form['file'].filename:
		return "Error: Please upload a file"

	ethmac   = "unset"
	password = "unset"
	if 'ethmac' in   req.form: ethmac   = req.form['ethmac']
	if 'password' in req.form: password = req.form['password']

	user = auth_user(ethmac,password)

	# Record which IP send this file
	ip = req.get_remote_host(apache.REMOTE_NOLOOKUP)

	return save_file(req.form['file'], ip, user)

def auth_user(mac, password):
	# shoulc check if this really is the user's MAC address

	# check Eth MAC is well-formed
	if not re.match("([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})",mac):
		return "unset"

	return mac

def save_file(fileitem, ip, user=None):
	# strip leading path from file name to avoid directory traversal attacks
	filename = NOW+".tgz"
	if user!=None:
		filename = user+"-"+filename
	#os.path.basename(fileitem.filename)

	# build absolute path to files directory
	host_dir = os.path.join(DUMP_DIR, ip)
	ensure_dir(host_dir)
	filepath = os.path.join(host_dir, filename)

	if os.path.exists(filepath):
		return "Error: file already exists"

	fd = open(filepath, 'wb')
	while 1:
        	chunk = fileitem.file.read(100000)
        	if not chunk: break
        	fd.write (chunk)
	return 'The file "%s" was uploaded successfully from  %s' % (filepath, ip)

def ensure_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)

