import os
import random
import sys
import cgi
import cgitb
cgitb.enable()
# to avoid showing errors to users use the following
#cgitb.enable(display=0, logdir="/path/to/logdir")

#form = cgi.FieldStorage()
dump_dir="/var/www/html/dump"
if not os.path.exists(dump_dir):
    print "making dir"
    os.makedirs(dump_dir)



def index(req):
   if not 'file' in req.form:
       return "Error: Please upload a file using"

   # A nested FieldStorage instance holds the file
   fileitem = req.form['file']

   # Test if the file was uploaded
   if fileitem.filename:
      # strip leading path from file name to avoid directory traversal attacks
      filename = os.path.basename(fileitem.filename)
      # build absolute path to files directory
      #dump_dir = os.path.join(os.path.dirname(filename), 'dump')
      open(os.path.join(dump_dir, filename), 'wb').write(fileitem.file.read())
      message = 'The file "%s" was uploaded successfully' % filename

   else:
      message = 'Error: No file was uploaded'
   return message
