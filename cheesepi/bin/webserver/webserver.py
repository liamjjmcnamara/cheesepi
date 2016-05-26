#!/usr/bin/env python

import os
import json
import cherrypy
from cherrypy.lib.static import serve_file

import cheesepi as cp

resultLimit = 5 # number of results per page
serveroot = os.path.dirname(os.path.realpath(__file__))
confpath  = os.path.join(serveroot,'cherrypy.conf')

def match_path(pathA, pathB):
	"""Ensure each member of pathB is matched in pathA (not reflexive!)"""
	if len(pathB)>len(pathA): return False
	for i in xrange(len(pathB)):
		if pathA[i]!=pathB[i]:
			return False
	return True


class RestAPI(object):
	exposed = True
	def serve_config_js(self):
		cherrypy.response.headers['Content-Type'] = "text/javascript"
		with open(os.path.join(serveroot,"config.js"), 'r') as f:
			content = f.read()
			ip = cp.utils.get_IP()
			return content.replace("INFLUXDB_IP",ip)

	def serve_default_json(self, **params):
		"""Serve the dashboard file, replace the WiFi AP"""
		cherrypy.response.headers['Content-Type'] = "application/json"
		with open(os.path.join(serveroot,"app","dashboards","default.json"), 'r') as f:
			content = f.read()
			essid = cp.config.get('ap')
			if essid==None: essid="ACCESSPOINTESSID"
			return content.replace("ACCESSPOINTESSID",essid)
		return "Error: Can't read default.json file"

	def serve_css(self, css):
		return serve_file(os.path.join(serveroot,"css",css))

	def serve_status(self):
		cherrypy.response.headers['Content-Type'] = "application/json"
		return json.dumps(cp.utils.get_status())
		return "{'bandwidth':50, 'tcp':75, 'udp':25, 'jitter':10}"

	def GET(self, *vpath, **params):
		if len(vpath)==2 and vpath[0]=="css": return self.serve_css(vpath[1])
		if match_path(vpath,["status.json"]): return self.serve_status()
		if match_path(vpath,["config.js"]):   return self.serve_config_js()
		if match_path(vpath,["app","dashboards","default.json"]):
			return self.serve_default_json()
		#if len(vpath)==1 and vpath[0]=="config.js": return self.serve_config_js()
		#if len(vpath)==3 and vpath[2]=="default.json": return self.serve_default_json()
		#cherrypy.response.headers['Content-Type'] = "text/javascript"

		filename="index.html"
		if len(vpath)>0:
			filename = "/".join(vpath)
		serve_path = os.path.join(serveroot,filename)
		print "Serving: %s" % serve_path
		return serve_file(serve_path)


def setup_server(port=8080):
	cherrypy.config.update({
		'global': {
			'environment': 'test_suite',
			'server.socket_host': '0.0.0.0',
			'server.socket_port': port,
		}
	})

	restconf = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()} }
	# start the cherrypy event loop
	cherrypy.quickstart(RestAPI(), '/', restconf)

if __name__ == "__main__":
	setup_server()
