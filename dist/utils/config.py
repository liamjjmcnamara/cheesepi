#!/usr/bin/env python
""" Copyright (c) 2015, Swedish Institute of Computer Science
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
"""

import sys
import os
import re

parent_dir  = os.path.dirname(os.path.realpath(__file__))
config_file = parent_dir + "/../cheesepi.conf"

def main():
    config = parse_config()
    print config


# clean the identifiers
def s(id):
    return id.strip().lower()


def read_config():
    try:
        fd = open(config_file)
        lines = fd.readlines()
    except Exception as e:
        print "Error: can not read config file: "+str(e)
        sys.exit(1)
    return lines


def parse_config():
    config = {}
    lines  = read_config()
    for line in lines:
        # strip comment and badly formed lines
        if re.match('^#', line) or not re.search('=',line):
            continue
        # print line
        (key, value) = line.split("=",2)
        config[s(key)] = s(value)
    return config


if __name__ == "__main__":
	main()
