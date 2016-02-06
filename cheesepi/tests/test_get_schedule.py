from __future__ import unicode_literals, absolute_import, print_function

from twisted.internet import defer
from txmsgpackrpc.client import connect

from pprint import pformat

@defer.inlineCallbacks
def call_get_schedule(uuid, num):
	print("Getting schedule for uuid: {}".format(uuid))
	try:
		c = yield connect('localhost', 18080, connectTimeout=5, waitTimeout=5)

		data = {
			'uuid':uuid,
			'num':num
		}

		res = yield c.createRequest('get_schedule', data)
		c.disconnect()
		defer.returnValue(res)
	except Exception as e:
		defer.returnValue(e)

@defer.inlineCallbacks
def main(uuid, num):

	from cheesepi.server.storage.models.target import Target

	result = yield call_get_schedule(uuid, num)

	schedule = []
	if result['status'] == 'success':
		for s in result['result']:
			schedule.append(Target.fromDict(s))
	else:
		print("Fail.. :(")

	print(schedule)

	print(pformat(result))

	reactor.stop()

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--uuid', type=str,
		help="The uuid of the node to get the schedule for")
	parser.add_argument('--num', type=int, default=1,
		help="The length of the schedule")

	args = parser.parse_args()

	if args.uuid is not None:
		from twisted.internet import reactor

		reactor.callWhenRunning(main, args.uuid, args.num)
		reactor.run()
	else:
		print("No uuid specified.")
