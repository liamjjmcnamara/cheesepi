#!/usr/bin/env python

import os
import logging
import socket
import cherrypy

from cherrypy.lib.static import serve_file


#logger = logging.getLogger(__name__)
#logger.setLevel(logging.ERROR)

quiet=False
if (quiet):
	cherrypy.log.error_log.setLevel(30)

resultLimit = 5 # number of results per page
serveroot = os.path.dirname(os.path.realpath(__file__))
confpath  = os.path.join(serveroot,'cherrypy.conf')
#print "Webserver root: "+serveroot

#serveroot = os.path.join(serveroot,"dashboard")
#print serveroot
#dao = cp.config.get_dao()

class Root:
	def index(self):
		raise cherrypy.HTTPRedirect("/dashboard")
		return
	index.exposed = True

class Dynamic:
	def index(self, **params):
		return serve_file(os.path.join(serveroot,"dashboard","index.html"))
		#cherrypy.response.headers["Content-Type"]  = "application/json"
		#return '{[{"value":10},{"value":15}]}'
		#return '{["value":1],["value":2]}'
		#return dao.get_op("ping")

	@cherrypy.expose
	def config_js(self, **params):
		"""Serve the config file, replace the local IP"""
		with open(os.path.join(serveroot,"dashboard","config.js"), 'r') as f:
			content = f.read()
			ip = cp.utils.get_IP()
			return content.replace("INFLUXDB_IP",ip)
		return "Error"

	def default(self, **name):
		path = os.path.join(serveroot,"dashboard",name)
		print path
		return serve_file(path)
	default.exposed = True
	index.exposed = True
	config_js.exposed = True

def setup_server(port=8080):
	root = Root()
	root.dashboard = Dynamic()
	config = { 'global': { 'environment': 'embedded', }, }
	for d in ["css","app","img","font","plugins"]:
		config["/dashboard/"+d] = {
			'tools.staticdir.on':    True,
			'tools.staticdir.root':  serveroot,
			'tools.staticdir.dir':   'dashboard/'+d,
			'tools.staticdir.index': 'index.html',
		}
	cherrypy.log.screen = False
	cherrypy.tree.mount(root, config=config)
	cherrypy.config.update({ 'server.socket_host':'0.0.0.0', 'server.socket_port':port, })
	try:
		cherrypy.server.start()
	except IOError as e:
		msg = "Error: Can't start server, port probably already in use: "+str(e)
		print msg
		logging.error(msg)

if __name__ == "__main__":
	setup_server()




