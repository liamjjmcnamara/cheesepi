#!/usr/bin/env python

import os
import logging
import socket
import cherrypy

from cherrypy.lib.static import serve_file

import cheesepi as cp

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.ERROR)

quiet=True
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
	@cherrypy.expose
	def index(self):
		print "root index"
		raise cherrypy.HTTPRedirect("/dashboard")
		return
	@cherrypy.expose
	def GET(self):
		return 'get root'

class Dashboard (object):
	exposed = True

	@cherrypy.expose
	def index(self, **params):
		print "Dash index %s" % params
		return serve_file(os.path.join(serveroot,"dashboard","index.html"))
		#cherrypy.response.headers["Content-Type"]  = "application/json"

	def GET(self):
		print "got"
		return 'get'

	@cherrypy.expose
	def config_js(self, **params):
		print "Dash config"
		"""Serve the config file, replace the local IP"""
		with open(os.path.join(serveroot,"dashboard","config.js"), 'r') as f:
			content = f.read()
			ip = cp.utils.get_IP()
			return content.replace("INFLUXDB_IP",ip)
		return "Error: Can't read config.js file"

	@cherrypy.expose
	def default(self, **name):
		print "Dash default %s" % name
		path = os.path.join(serveroot,"dashboard",name)
		return serve_file(path)

	@cherrypy.expose
	def css(self, **name):
		print "Dash css %s" % name
		path = os.path.join(serveroot,"dashboard",name)
		return serve_file(path)

	@cherrypy.expose
	def app(self, **name):
		print "Dash app %s" % name
		path = os.path.join(serveroot,"dashboard",name)
		return serve_file(path)

class JSON:
	@cherrypy.expose
	def default_json(self, **params):
		print "JSON default json"
		"""Serve the dashboard file, replace the WiFi AP"""
		with open(os.path.join(serveroot,"dashboard","app","dashboards","default.json"), 'r') as f:
			content = f.read()
			essid = cp.config.get('ap')
			if essid==None: essid="ACCESSPOINTESSID"
			return content.replace("ACCESSPOINTESSID",essid)
		return "Error: Can't read default.json file"

	@cherrypy.expose
	def default(self, **name):
		print "JSON default %s" % name
		path = os.path.join(serveroot,"dashboard","app","dashboards",name)
		return serve_file(path)


def setup_server(port=8080):
	#root = Root()
	#root.dashboard = Dashboard()
	#root.dashboard.app.dashboards = JSON()
	config = { 'global': { 'environment': 'embedded', },
		'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()},
		}

	config2={}
	for d in ["css","app","img","font","plugins"]:
		config2["/dashboard/"+d] = {
			'tools.staticdir.on':    True,
			'tools.staticdir.root':  serveroot,
			'tools.staticdir.dir':   'dashboard/'+d,
			'tools.staticdir.index': 'index.html',
		}
	cherrypy.log.screen = False
	cherrypy.tree.mount(Root(), '/')
	cherrypy.tree.mount(Dashboard(), '/dashboard', config=config)
	#cherrypy.tree.mount(JSON(), '/dashboard/app/dashboards', config=config)
	cherrypy.config.update({ 'server.socket_host':'0.0.0.0', 'server.socket_port':port, })
	try:
		cherrypy.server.start()
	except IOError as e:
		msg = "Error: Can't start server, port probably already in use: "+str(e)
		print msg
		logging.error(msg)

if __name__ == "__main__":
	setup_server()




