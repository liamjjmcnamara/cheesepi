#!/usr/bin/env python
""" Copyright (c) 2016, Swedish Institute of Computer Science
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
	  * Redistributions of source code must retain the above copyright
		notice, this list of conditions and the following disclaimer.
	  * Redistributions in binary form must reproduce the above copyright
		notice, this list of conditions and the following disclaimer in the
		documentation and/or other materials provided with the distribution.
	  * Neither the name of The Swedish Institute of Computer Science nor the
		names of its contributors may be used to endorse or promote products
		derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE SWEDISH INSTITUTE OF COMPUTER SCIENCE BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Authors: ljjm@sics.se
Testers:
Description: Handles all configuration file duties, including initialising
a local config file (if one does not exist), and initialising logging options
"""

import os
from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

def version():
	with open(os.path.join('cheesepi','VERSION')) as f:
		return f.read().strip()

setup(
	name='cheesepi',
	description='CheesePi Library',
	long_description=readme(),
	version=version(),
	url='http://cheesepi.sics.se',
	packages=['cheesepi'],
	author='Liam McNamara',
	author_email='ljjm@sics.se',
	license= 'Apache 2.0',
	platforms = ["RaspberryPi"],
	classifiers=[
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: POSIX',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Topic :: Internet',
		'Topic :: System :: Logging',
	],

	# Runtime dependencies
	install_requires=[
		'setuptools',
		'pip',
		'future',
		'argparse',
		'influxdb',
		'cherrypy',
		'uptime',
		'dnspython',
		'youtube_dl',
		'speedtest-cli',
	],
	extras_require = {
		'extra' : ['txmsgpackrpc','twisted','netifaces','pymongo'],
	},

	entry_points={
		'console_scripts':[
			'cheesepi = cheesepi.utils:console_script',
		]
	},
	include_package_data=True,
	zip_safe=False,
)
