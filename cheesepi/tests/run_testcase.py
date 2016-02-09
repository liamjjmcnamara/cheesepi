#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, print_function

import json
import os
import time
import tarfile
import requests
import hashlib
import math
import numpy as np

import matplotlib.pyplot as plt

from pprint import pformat

from mprpc import RPCClient

import mock_ping as mp

# Changes later
DIRNAME="testcase_dir/"


def md5_filehash(filepath):
	hasher = hashlib.md5()
	with open(filepath) as fd:
		hasher.update(fd.read())
	return hasher.hexdigest()


def call_get_schedule(uuid, num, method="smart"):
	print("Getting schedule for uuid: {}".format(uuid))

	data = {
		'uuid':uuid,
		'num':num,
		'method':method
	}

	client = RPCClient(b'localhost', 18080)
	result = client.call(b'get_schedule', data)
	client.close()

	return result


def call_register(uuid):
	print("Registering peer with uuid: {}".format(uuid))

	client = RPCClient(b'localhost', 18080)
	res = client.call(b'register', uuid)
	client.close()

	return res


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
			json.dump(dict_object, fd)

		upload_results(uuid, result_path, tar_dir)


def upload_results(uuid, source_file, tar_dir):
	# Tar the results
	tarname = uuid + ".tgz"
	tarpath = os.path.join(tar_dir, tarname)

	with tarfile.open(name=tarpath, mode='w:gz') as tar:
		tar.add(source_file, arcname='ping.json')

	md5_hash = md5_filehash(tarpath)

	# Upload tar file
	url = 'http://localhost:18090/upload'
	params = {
		'filename':tarname,
		'md5_hash':md5_hash,
	}
	files = {'file':open(tarpath, 'rb')}

	response = requests.post(url, params, files=files)

	return response


def peer_pass(peer, peer_dir, tar_dir, sched_size, sample_size, schedule_method='smart'):

	uuid = peer.get_uuid()

	os.mkdir(peer_dir)


	# Result file
	result_path = os.path.join(peer_dir, "ping.json")

	sched = call_get_schedule(uuid, sched_size, method=schedule_method)
	#print(sched)

	uuid_sched = [target['uuid'] for target in sched['result']]
	puf = mp.PingUploadConstructor(uuid)

	#print("Got schedule:\n{}".format(pformat(uuid_sched)))
	for target in sched['result']:
		target_uuid = target['uuid']
		target_ip = target['ip']

		samples = peer.sample_link(target_uuid, sample_size)
		#print("Generated samples for target {}\n{}".format(target_uuid,
			#pformat(samples)))
		puf.add_result(samples, target_uuid, target_ip)

	dict_object = puf.construct()

	# Write the data to file
	with open(result_path, "w") as fd:
		json.dump(dict_object, fd)

	print("Uploading results for {}".format(uuid))
	result = upload_results(uuid, result_path, tar_dir)
	print(result)

	return peer


def measurement_pass(peers, pass_dir, schedule_method='smart'):

	tar_dir = os.path.join(pass_dir, "tar")

	os.mkdir(pass_dir)
	os.mkdir(tar_dir)

	modified_peers = []

	for peer in peers:
		uuid = peer.get_uuid()

		peer_dir = os.path.join(pass_dir, uuid)

		mod_peer = peer_pass(peer, peer_dir, tar_dir, sched_size, sample_size,
				schedule_method=schedule_method)

		#print(pformat(mod_peer.dms))

		modified_peers.append(mod_peer)

	return modified_peers


def register_peers(peers):
	for peer in peers:
		call_register(peer.get_uuid())


def main_loop(peers, iterations=1, sched_size=1, sample_size=10,
		schedule_method="smart", full_coverage_start=False):

	print("Running test with {} iterations ".format(iterations) +
		"with schedules of size {} ".format(sched_size) +
		"and sample size of {}".format(sample_size))

	# Make sure the peers are present as entities in the database
	results = register_peers(peers)
	#print(results)

	if full_coverage_start:
		results = full_coverage_pass(peers, sample_size)
		#print(results)

	# Maybe initialize with one iteration complete coverage???

	for i in range(0, iterations):
		# Create directory
		ITER_DIR = os.path.join(DIRNAME, str(i))

		peers = measurement_pass(peers, ITER_DIR, schedule_method=schedule_method)

	# If we don't sleep there's a possibility that the last data written
	# doesn't get taken into account when querying the database. There shouldn't
	# be any race conditions on the server however.... I think...
	print("DONE. Sleeping so database can catch up...")
	time.sleep(1)

	from cheesepi.server.storage.mongo import MongoDAO
	from cheesepi.server.storage.models.PingStatistics import PingStatistics

	from statsmodels.sandbox.distributions.extras import pdf_mvsk

	dao = MongoDAO()

	peer_stats = []

	# Plot stuff
	xmin = 0
	xmax = 100
	x_plot = np.linspace(xmin, xmax, xmax-xmin)

	num_peers = len(peers)

	#fig, plots = plt.subplots(num_peers, (num_peers-1)*3, sharex='col')

	for peer_index, peer in enumerate(peers):
		#plt.figure(peer_index+1)
		fig, plots = plt.subplots((num_peers-1), 3, sharex='col')
		fig.suptitle(peer.get_uuid())
		#peer_plot = plots[peer_index]
		#print(peer)
		#print(pformat(peer.dms))
		#print(peer._dm2)
		#print(peer._dm3)
		#print(peer._dm4)

		peer_uuid = peer.get_uuid()
		print("SOURCE: {}".format(peer_uuid))

		stats = dao.get_all_stats(peer.get_uuid())
		for stat_index, stat in enumerate(stats):
			assert isinstance(stat, PingStatistics)
			plot_row = plots[stat_index]

			stat_plot = plot_row[0]
			mv_plot = plot_row[1]
			sk_plot = plot_row[2]
			#stat_plot = peer_plot[stat_index]
			#mv_plot = peer_plot[stat_index + (num_peers-1)]
			#sk_plot = peer_plot[stat_index + 2*(num_peers-1)]

			target_uuid = stat.get_target().get_uuid()

			print("TARGET: {}".format(target_uuid))

			delay_model = stat.get_delay()

			#print(delay_model._dm1)
			#print(delay_model._dm2)
			#print(delay_model._dm3)
			#print(delay_model._dm4)

			num_samples = delay_model._n

			print("m={}, v={}, s={}, k={}".format(delay_model._m1,
				delay_model._new_variance, delay_model._skew, delay_model._kurtosis))

			pdf = pdf_mvsk([delay_model._m1, delay_model._new_variance,
					delay_model._skew, delay_model._kurtosis])

			orig_dist = peer.get_link(target_uuid).get_dist()

			y_model_plot = np.array([pdf(x) for x in x_plot])
			y_orig_plot = orig_dist.pdf(x_plot)

			stat_plot.text(0.50, 0.40, "#samples={}".format(num_samples),
					fontsize=8, transform=stat_plot.transAxes)

			# Distribution plots
			stat_plot.plot(x_plot, y_model_plot, color='r', label='model distribution')
			stat_plot.plot(x_plot, y_orig_plot,  color='b', label='original distribution')
			stat_plot.set_title("{}...".format(target_uuid[:20]), fontdict={'fontsize':10})
			stat_plot.legend(loc='upper right', ncol=1, fontsize=9)

			# Mean and variance plots
			print()
			print()
			print()
			print(*zip(*delay_model._dm1))
			print(*zip(*delay_model._dm2))
			mv_plot.plot(*zip(*delay_model._dm1), label=r'$\Delta$mean')
			mv_plot.plot(*zip(*delay_model._dm2), label=r'$\Delta$variance')
			mv_plot.set_title("{}...".format(target_uuid[:20]), fontdict={'fontsize':10})
			mv_plot.legend(loc='upper right', ncol=1, fontsize=9)

			# Skew and kurtosis plots
			print()
			print()
			print()
			print(delay_model._dm1)
			print(delay_model._dm2)
			sk_plot.plot(*zip(*delay_model._dm3), label=r'$\Delta$skew')
			sk_plot.plot(*zip(*delay_model._dm4), label=r'$\Delta$kurtosis')
			sk_plot.set_title("{}...".format(target_uuid[:20]), fontdict={'fontsize':10})
			sk_plot.legend(loc='upper right', ncol=1, fontsize=9)

	plt.show()



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


		main_loop(peers, iterations, sched_size, sample_size, sched_method,
				full_coverage_start)

	else:
		print("No file...")
