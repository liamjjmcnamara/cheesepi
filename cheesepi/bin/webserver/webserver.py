#!/usr/bin/env python

import os
import logging
import cherrypy


#logger = logging.getLogger(__name__)
#logger.setLevel(logging.ERROR)

cherrypy.log.error_log.setLevel(30)

resultLimit = 5 # number of results per page
serveroot = os.path.dirname(os.path.realpath(__file__))
confpath  = os.path.join(serveroot,'cherrypy.conf')
#print "Webserver root: "+serveroot

#dao = cp.config.get_dao()

class Root:
	def index(self):
		raise cherrypy.HTTPRedirect("/dashboard")
		return
	index.exposed = True

class Dynamic:
	def index(self, **params):
		cherrypy.response.headers["Content-Type"]  = "application/json"
		return '{[{"value":10},{"value":15}]}'
		#return '{["value":1],["value":2]}'
		#return dao.get_op("ping")
	index.exposed = True

def setup_server():
	root = Root()
	root.data = Dynamic()
	config = {
		'global': {
			'environment': 'embedded',
			'log.screen': False,
		},
		'/dashboard': {
			'log.screen': False,
			'tools.staticdir.on': True,
			'tools.staticdir.root': serveroot,
			'tools.staticdir.dir': 'dashboard',
			'tools.staticdir.index': 'index.html',
		},
		}
	cherrypy.log.screen = False
	cherrypy.tree.mount(root, config=config)
	cherrypy.config.update({ 'server.socket_host':'0.0.0.0', 'server.socket_port':8080, })
	try:
		cherrypy.server.start()
	except IOError as e:
		msg = "Error: Can't start server, port probably already in use: "+str(e)
		print msg
		logging.error(msg)

if __name__ == "__main__":
	setup_server()




