#!/usr/bin/env python2
from __future__ import unicode_literals, absolute_import, print_function

import json
import os
import time
import tarfile
import requests
import hashlib
import numpy as np

import matplotlib.pyplot as plt

from pprint import pformat

from twisted.internet import defer
from txmsgpackrpc.client import connect

import mock_ping as mp

# Changes later
DIRNAME="testcase_dir/"

def md5_filehash(filepath):
	hasher = hashlib.md5()
	with open(filepath) as fd:
		hasher.update(fd.read())
	return hasher.hexdigest()

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
def call_register(uuid):
	print("Registering peer with uuid: {}".format(uuid))
	try:
		c = yield connect('localhost', 18080, connectTimeout=5, waitTimeout=5)

		res = yield c.createRequest('register', uuid)
		c.disconnect()
		defer.returnValue(res)
	except Exception as e:
		defer.returnValue(e)

@defer.inlineCallbacks
def full_coverage_pass(peers, sample_size):
	print("Running full coverage pass")
	start_dir = os.path.join(DIRNAME, "start")
	tar_dir = os.path.join(start_dir, "tar")

	os.mkdir(start_dir)
	os.mkdir(tar_dir)

	for peer in peers:
		uuid = peer.get_uuid()
		puf = mp.PingUploadConstructor(uuid)

		peer_dir = os.path.join(start_dir, uuid)
		os.mkdir(peer_dir)
		result_path = os.path.join(peer_dir, "ping.json")

		for link in peer._links.itervalues():
			target_uuid = link._target_uuid
			samples = link.sample_dist(sample_size)
			print("Generated samples for target {}\n{}".format(target_uuid,
				pformat(samples)))
			puf.add_result(samples, target_uuid, "127.0.0.1")

		dict_object = puf.construct()

		# Write the data to file
		with open(result_path, "w") as fd:
			yield json.dump(dict_object, fd)

		upload_results(uuid, result_path, tar_dir)


@defer.inlineCallbacks
def upload_results(uuid, source_file, tar_dir):
	# Tar the results
	tarname = uuid + ".tgz"
	tarpath = os.path.join(tar_dir, tarname)
	#print(tarpath)
	with tarfile.open(name=tarpath, mode='w:gz') as tar:
		tar.add(source_file, arcname='ping.json')

	md5_hash = yield md5_filehash(tarpath)

	# Upload tar file
	url = 'http://localhost:18090/upload'
	params = {
		'filename':tarname,
		'md5_hash':md5_hash,
	}
	files = {'file':open(tarpath, 'rb')}

	print("Uploading results for {}".format(uuid))
	response = yield requests.post(url, params, files=files)

	defer.returnValue(response)

@defer.inlineCallbacks
def peer_pass(peer, peer_dir, tar_dir, sched_size, sample_size):

	uuid = peer.get_uuid()

	os.mkdir(peer_dir)

	# Result file
	result_path = os.path.join(peer_dir, "ping.json")

	sched = yield call_get_schedule(uuid, sched_size)

	uuid_sched = [target['uuid'] for target in sched['result']]
	puf = mp.PingUploadConstructor(uuid)

	print("Got schedule:\n{}".format(pformat(uuid_sched)))
	for target in sched['result']:
		target_uuid = target['uuid']
		target_ip = target['ip']

		samples = peer.sample_link(target_uuid, sample_size)
		print("Generated samples for target {}\n{}".format(target_uuid,
			pformat(samples)))
		puf.add_result(samples, target_uuid, target_ip)

	dict_object = puf.construct()

	# Write the data to file
	with open(result_path, "w") as fd:
		json.dump(dict_object, fd)

	# TODO Am I sure everything will happen sequentially??????
	# Yeah pretty sure, since twisted shouldn't introduce race conditions...
	upload_results(uuid, result_path, tar_dir)

@defer.inlineCallbacks
def measurement_pass(peers, pass_dir):

	tar_dir = os.path.join(pass_dir, "tar")

	os.mkdir(pass_dir)
	os.mkdir(tar_dir)

	for peer in peers:
		uuid = peer.get_uuid()

		peer_dir = os.path.join(pass_dir, uuid)

		yield peer_pass(peer, peer_dir, tar_dir, sched_size, sample_size)

@defer.inlineCallbacks
def register_peers(peers):
	for peer in peers:
		result = yield call_register(peer.get_uuid())

@defer.inlineCallbacks
def main_loop(peers, iterations=1, sched_size=1, sample_size=10,
		schedule_method="smart", full_coverage_start=False):

	print("Running test with {} iterations ".format(iterations) +
	      "with schedules of size {} ".format(sched_size) +
	      "and sample size of {}".format(sample_size))

	# Make sure the peers are present as entities in the database
	yield register_peers(peers)

	if full_coverage_start:
		full_coverage_pass(peers, sample_size)

	# Maybe initialize with one iteration complete coverage???

	for i in range(0, iterations):
		# Create directory
		ITER_DIR = os.path.join(DIRNAME, str(i))
		#TAR_DIR = os.path.join(ITER_DIR,"tar")

		#os.mkdir(ITER_DIR)
		#os.mkdir(TAR_DIR)

		yield measurement_pass(peers, ITER_DIR)

		#for peer in peers:
			#uuid = peer.get_uuid()

			#peer_dir = os.path.join(ITER_DIR, uuid)
			#peer_pass(peer, peer_dir, sched_size, sample_size)

			# Create directory
			# PEER_DIR = os.path.join(ITER_DIR, uuid)
			# os.mkdir(PEER_DIR)

			# # Result file
			# PEER_RESULT = os.path.join(PEER_DIR, "ping.json")

			# sched = yield call_get_schedule(uuid, sched_size)

			# uuid_sched = [target['uuid'] for target in sched['result']]
			# puf = mp.PingUploadConstructor(uuid)

			# print("Got schedule:\n{}".format(pformat(uuid_sched)))
			# for target in sched['result']:
			# 	target_uuid = target['uuid']
			# 	target_ip = target['ip']

			# 	samples = peer.sample_link(target_uuid, sample_size)
			# 	print("Generated samples for target {}\n{}".format(target_uuid,
			# 		pformat(samples)))
			# 	puf.add_result(samples, target_uuid, target_ip)

			# dict_object = puf.construct()

			# # Write the data to file
			# with open(PEER_RESULT, "w") as fd:
			# 	json.dump(dict_object, fd)

			# # Tar the results
			# tarname = uuid + ".tgz"
			# tarpath = os.path.join(TAR_DIR, tarname)
			# #print(tarpath)
			# with tarfile.open(name=tarpath, mode='w:gz') as tar:
			# 	tar.add(PEER_RESULT, arcname='ping.json')

			# md5_hash = md5_filehash(tarpath)

			# # Upload tar file
			# url = 'http://localhost:18090/upload'
			# params = {
			# 	'filename':tarname,
			# 	'md5_hash':md5_hash,
			# }
			# files = {'file':open(tarpath, 'rb')}

			# response = requests.post(url, params, files=files)
			#data = urllib.urlencode(params)
			#request = urllib2.Request(url, data)
			#response = urllib2.urlopen(request)
			#body = response.read()
			#print(response.text)

		# Ugly way to try to avoid race conditions in the server...
		# Maybe not needed...
		#time.sleep(1)

	print("DONE")
	from cheesepi.server.storage.mongo import MongoDAO
	from cheesepi.server.storage.models.PingStatistics import PingStatistics

	from statsmodels.sandbox.distributions.extras import pdf_mvsk

	dao = MongoDAO()

	peer_stats = []
	pdfs = []

	# Plot stuff
	xmin = 0
	xmax = 100
	x_plot = np.linspace(xmin, xmax, xmax-xmin)

	num_peers = len(peers)

	fig, plots = plt.subplots(num_peers, num_peers-1, sharex='col', sharey='row')

	for peer_index, peer in enumerate(peers):
		peer_plot = plots[peer_index]
		print(peer)

		peer_uuid = peer.get_uuid()

		stats = dao.get_all_stats(peer.get_uuid())
		for stat_index, stat in enumerate(stats):
			assert isinstance(stat, PingStatistics)
			stat_plot = peer_plot[stat_index]

			target_uuid = stat.get_target().get_uuid()

			print(target_uuid)

			delay_model = stat.get_delay()
			print("m={}, v={}, s={}, k={}".format(delay_model._m1,
				delay_model._new_variance, delay_model._skew, delay_model._kurtosis))

			pdf = pdf_mvsk([delay_model._m1, delay_model._new_variance,
					delay_model._skew, delay_model._kurtosis])

			orig_dist = peer.get_link(target_uuid).get_dist()

			#pdfs.append(pdf)
			y_model_plot = np.array([pdf(x) for x in x_plot])
			y_orig_plot = orig_dist.pdf(x_plot)

			#stat_plot = fig.add_subplot(pn,1,1)
			stat_plot.plot(x_plot, y_model_plot, color='r', label='model distribution')
			stat_plot.plot(x_plot, y_orig_plot,  color='b', label='original distribution')
			stat_plot.set_title("{}... -> {}...".format(peer_uuid[:8],
				target_uuid[:8]), fontdict={'fontsize':10})
			#stat_plot.legend(peer.get_uuid() + " -> " + stat.get_target().get_uuid())
			stat_plot.legend(loc='upper right', ncol=1, fontsize=10)

	plt.show()


	#print(pdfs)

	reactor.stop()


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()

	parser.add_argument('--file',type=str,default=None,
		help="file with testcase defined in JSON")

	args = parser.parse_args()

	if args.file is not None:
		with open(args.file) as fd:
			json_obj = json.load(fd)

		DIRNAME = os.path.abspath(args.file.split(".")[0])
		os.mkdir(DIRNAME)

		peers = []

		for peer in json_obj['peers']:
			pm = mp.PeerMocker.fromDict(peer)
			peers.append(pm)

		iterations = json_obj['iterations']
		sample_size = json_obj['sample_size']
		sched_size = json_obj['schedule_size']
		sched_method = json_obj['schedule_method']
		full_coverage_start =  ("True" == json_obj['full_coverage_start'])


		from twisted.internet import reactor
		reactor.callWhenRunning(main_loop, peers, iterations, sched_size,
				sample_size, sched_method, full_coverage_start)
		reactor.run()
		#print(dir(mp))
		#pm = mp.GammaDist()
		#print(pm.sample_n(100))


		#import matplotlib.pyplot as plt
		#dist = pm.get_dist()
		#x = [i for i in range(0, 50)]
		#plt.plot(x, dist.pdf(x))
		#plt.show()

		# Now do something with the json object...
	else:
		print("No file...")
