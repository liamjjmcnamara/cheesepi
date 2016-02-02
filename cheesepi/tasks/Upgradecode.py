from __future__ import unicode_literals
import os
from time import time
import pip

import cheesepi
import Task

logger = cheesepi.utils.get_logger(__name__)


class Upgradecode(Task.Task):
	"""Update to latest version of the CheesePi code"""

	# construct the process and perform pre-work
	def __init__(self, dao, spec={}):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "upgradecode"

	def run(self):
		logger.info("Updating pip and cheesepi, @ %d PID: %d" % (time(), os.getpid()))
		self.pip_upgrade()

	def pip_upgrade(self):
		pass


def main(peer_id):
	upgrade_task = Upgradecode(None)
	upgrade_task.run()


if __name__ == "__main__":
	main()
