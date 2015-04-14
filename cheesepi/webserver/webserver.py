#!/usr/bin/python

import os
import logging
import cherrypy

import cheesepi

resultLimit = 5 # number of results per page

serveroot = os.path.dirname(os.path.realpath(__file__))

confpath = os.path.join(serveroot,'cherrypy.conf')
print "Server root: "+serveroot

dao = cheesepi.storage.DAO()

def setup_server():

	class Root:
		def index(self):
			return
		index.exposed = True

	class Dynamic:
		def index(self, **params):
			cherrypy.response.headers["Content-Type"]  = "application/json"
			return '{[{"value":10},{"value":15}]}'
			return '{["value":1],["value":2]}'
			return dao.get_op("ping")
		index.exposed = True
		#def dynamic(self):
		#	return "This is a DYNAMIC page"
		#dynamic.exposed = True

	root = Root()
	root.data = Dynamic()
	config = {
		'global': {
			'environment': 'production',
			'log.screen': True,
			'server.socket_port': 9999,
		},
		'/dashboard': {
			'tools.staticdir.on': True,
			'tools.staticdir.root': serveroot,
			'tools.staticdir.dir': 'dashboard',
			'tools.staticdir.index': 'index.html',
		},
		}
	cherrypy.tree.mount(root, config=config)
	cherrypy.config.update({ 'server.socket_host':'0.0.0.0', 'server.socket_port':8080, })
	try:
		cherrypy.server.start()
	except IOError as e:
		msg = "Error: Can't start server, port probably already in use: "+str(e)
		print msg
		logging.error(msg)

setup_server()




