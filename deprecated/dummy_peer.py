from __future__ import print_function, unicode_literals

from builtins import str

from txmsgpackrpc.client import connect

from twisted.internet import defer

from time import time

@defer.inlineCallbacks
def callRegister(peer_id):
    c = yield connect('localhost', 18080, connectTimeout=5, waitTimeout=5)

    res = yield c.createRequest('register', peer_id)
    c.disconnect()
    defer.returnValue(res)

@defer.inlineCallbacks
def callGetTasks(peer_id):
    c = yield connect('localhost', 18080, connectTimeout=5, waitTimeout=5)
    result = yield c.createRequest('get_tasks', peer_id)
    c.disconnect()
    defer.returnValue(result)

@defer.inlineCallbacks
def callUploadResult(result_data):
    c = yield connect('localhost', 18080, connectTimeout=5, waitTimeout=5)
    res = yield c.createRequest('upload_result', result_data)
    c.disconnect()
    defer.returnValue(res)

@defer.inlineCallbacks
def cmdline(command):
    from subprocess import PIPE, Popen
    process = yield Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    defer.returnValue(process.communicate()[0])

@defer.inlineCallbacks
def main(peer_id):
    from twisted.internet import reactor
    import time
    import os
    import re
    from random import randint

    register_response = yield callRegister(peer_id)

    while True:
        tasks_response = yield callGetTasks(peer_id)

        # If we fail, it might be because we are not registered
        if tasks_response['status'] == 'failure':
            if tasks_response['error'] == 'nosuchpeer':
                registered_response = yield callRegister(peer_id)
                tasks_response = yield callGetTasks(peer_id)
            else:
                # Something went horribly wrong
                print(tasks_response['error'])
                exit()

        tasks = tasks_response['result']
        print("got {} new tasks".format(len(tasks)))

        for task in tasks:
            task_output = yield cmdline('ping -qnc 5 ' + task['target_host'])
            #print(task_output)
            task_pattern = re.compile(r"""
                    ^rtt\ min/avg/max/mdev\ =\  # start of line
                    (\d+\.\d*)/   # min
                    (\d+\.\d*)/   # avg
                    (\d+\.\d*)/   # max
                    (\d+\.\d*)    # mdev
                    """,
                    re.MULTILINE | re.VERBOSE)
            task_match = task_pattern.search(task_output)
            #if task_match:
                #print("Matched: {}".format(task_match.groups()))
            #else:
                #print("No match...")

            time.sleep(5)
            result_data = {
                'peer_id':peer_id,
                'result':{
                    'target_id':task['target_id'],
                    'task_id':task['task_id'],
                    'task_name':'ping',
                    'value':task_match.group(2),
                    'timestamp':time.time()
                    }
            }

            print("sending result for task {}: ping to {}".format(
                task['task_id'],
                task['target_id'])
            )

            upload_response = yield callUploadResult(result_data)
            print("Upload Response: {}".format(upload_response['status']))

        time.sleep(5)

    reactor.stop()

if __name__ == "__main__":
    from twisted.internet import reactor
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default=None,
                        help='peer id')

    args = parser.parse_args()

    if args.id is None:
        exit()

    reactor.callWhenRunning(main, args.id)
    reactor.run()
