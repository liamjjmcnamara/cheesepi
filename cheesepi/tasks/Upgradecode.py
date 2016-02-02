from __future__ import unicode_literals
import os
from time import time
import pip

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)


class Upgradecode(Task.Task):
	"""Update to latest version of the CheesePi code"""

	# construct the process and perform pre-work
	def __init__(self, dao=None, spec={}):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "upgradecode"

	def run(self):
		logger.info("Updating pip and cheesepi, @ %d PID: %d" % (time(), os.getpid()))
		pip.main(['install', '--upgrade', "cheesepi"])

	def pip_upgrade(self):
		pass


def main():
	upgrade_task = Upgradecode()
	upgrade_task.run()


if __name__ == "__main__":
	main()
