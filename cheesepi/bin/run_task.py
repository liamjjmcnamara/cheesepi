#!/usr/bin/env python

import sys
import argparse

import cheesepi

parser = argparse.ArgumentParser()
parser.add_argument('--task', type=str, default=None, help='Task spec')

args = parser.parse_args()
if args.task is None:
    print("Error: missing --task argument")
    sys.exit(0)

dao = cheesepi.storage.get_dao()
task = cheesepi.utils.build_json(dao, args.task)

if task is None:
    print("Task spec does not seem valid: " + args.task)
    sys.exit(1)

task.run()
