#!/usr/bin/env python

from __future__ import unicode_literals, absolute_import, print_function

import argparse

import cheesepi as cp

parser = argparse.ArgumentParser()

parser.add_argument('--task', type=str, default=None,
                    help='Task spec')

args = parser.parse_args()
if args.task == None:
	print("Error: missing --task argument")
	exit(0)

dao = cp.config.get_dao()
task = cp.utils.build_json(dao, args.task)

if task==None:
	print("Task spec does not seem valid: "+args.task)
	exit(1)

task.run()
