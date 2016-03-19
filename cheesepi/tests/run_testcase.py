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
import datasets as ds

from cheesepi.server.storage.mongo import MongoDAO
from cheesepi.server.storage.models.statistics import StatisticsSet

# Changes later
ROOTDIR="testcase_dir/"


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


def full_coverage_pass(peers, sample_size, iteration):
	print("Running full coverage pass")
	start_dir = os.path.join(DUMPDIR, "{}_full".format(str(iteration)))
	tar_dir = os.path.join(start_dir, "tar")

	os.mkdir(start_dir)
	os.mkdir(tar_dir)

	new_peers = []

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

		# Update stats
		dao = MongoDAO()
		old_stats = StatisticsSet()
		new_stats = dao.get_all_stats(uuid)

		peer = update_stats_for_links(peer, iteration, old_stats, new_stats)
		new_peers.append(peer)

		dao.close()

	return new_peers


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

def update_stats_for_links(peer, iteration, old_stats, new_stats):
	# In the data we don't want 0-indexing
	index = iteration + 1

	for target_uuid, link in peer._links.iteritems():
		old = old_stats.get_stats_for_target(target_uuid)
		new = new_stats.get_stats_for_target(target_uuid)

		# We know we're only getting one type of stat (ping)
		old = None if len(old) == 0 else old[0]
		new = None if len(new) == 0 else new[0]

		# TODO if nothing has changed, the deltas should just be copies of the
		# previous values
		if new:
			nd = new.get_delay()

			um = nd._uni_mean
			uv = nd._uni_variance
			em = nd._exp_mean
			ev = nd._exp_variance
			#m = nd._m1
			#v = nd._new_variance
			# s = nd._skew
			# k = nd._kurtosis

			dum = None
			duv = None
			dem = None
			dev = None

			if old:
				od = old.get_delay()

				if (od._n < nd._n):
					dum = math.fabs(od._uni_mean - um)
					duv = math.fabs(od._uni_variance - uv)
					#dm = math.fabs(od._m1 - m)
					#dv = math.fabs(od._new_variance - v)
					dem = math.fabs(od._exp_mean - em)
					dev = math.fabs(od._exp_variance - ev)
				else:
					# Nothing has changed, keep old values
					#print("NOTHING HAPPENED")
					pass
			else:
				# First iteration
				dum = um
				duv = uv
				dem = em
				dev = ev

			link.add_historical_model_data(index, um, uv, em, ev, dum, duv, dem, dev)
		#elif new:
			# Deltas are now the same as the values since we start from 0
			#d = new.get_delay()
			#link.add_historical_model_data(iteration, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)
		else:
			# Nothing to do???
			# Maybe default everything to 0...
			#link.add_historical_model_data(index)
			pass
	return peer


def peer_pass(peer, peer_dir, tar_dir, sched_size, sample_size, iteration,
		schedule_method='smart'):

	uuid = peer.get_uuid()

	os.mkdir(peer_dir)

	dao = MongoDAO()

	old_stats = dao.get_all_stats(uuid)

	# Result file
	result_path = os.path.join(peer_dir, "ping.json")

	sched = call_get_schedule(uuid, sched_size, method=schedule_method)
	#print(sched)

	uuid_sched = [target['uuid'] for target in sched['result']]
	puf = mp.PingUploadConstructor(uuid)

	print("Got schedule:\n{}".format(pformat(uuid_sched)))
	for target in sched['result']:
		target_uuid = target['uuid']
		target_ip = target['ip']

		samples = peer.sample_link(target_uuid, sample_size, iteration)
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

	new_stats = dao.get_all_stats(uuid)

	peer = update_stats_for_links(peer, iteration, old_stats, new_stats)

	# TODO This is where deltas could be calculated!!!
	#print(old_stats)
	#print(new_stats)

	dao.close()

	return peer


def measurement_pass(peers, pass_dir, iteration, schedule_method='smart'):

	tar_dir = os.path.join(pass_dir, "tar")

	os.mkdir(pass_dir)
	os.mkdir(tar_dir)

	modified_peers = []

	for peer in peers:
		uuid = peer.get_uuid()

		peer_dir = os.path.join(pass_dir, uuid)

		mod_peer = peer_pass(peer, peer_dir, tar_dir, sched_size, sample_size,
				iteration, schedule_method=schedule_method)

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

	iteration_index = 0

	if full_coverage_start:
		peers = full_coverage_pass(peers, sample_size, iteration_index)
		iteration_index = iteration_index + 1
		#print(results)

	# Maybe initialize with one iteration complete coverage???

	for i in range(0, iterations):
		# Create directory
		ITER_DIR = os.path.join(DUMPDIR, str(iteration_index))

		peers = measurement_pass(peers, ITER_DIR, iteration_index, schedule_method=schedule_method)
		iteration_index = iteration_index + 1

	# If we don't sleep there's a possibility that the last data written
	# doesn't get taken into account when querying the database. There shouldn't
	# be any race conditions on the server however.... I think...
	print("DONE. Sleeping so database can catch up...")
	time.sleep(1)

	from cheesepi.server.storage.mongo import MongoDAO
	from cheesepi.server.storage.models.PingStatistics import PingStatistics

	from statsmodels.sandbox.distributions.extras import pdf_mvsk

	dao = MongoDAO()

	for peer_index, peer in enumerate(peers):
		print(peer_index)

		peer_uuid = peer.get_uuid()
		print("SOURCE: {}".format(peer_uuid))

		stats = dao.get_all_stats(peer.get_uuid())
		for stat_index, stat in enumerate(stats):
			assert isinstance(stat, PingStatistics)

			target_uuid = stat.get_target().get_uuid()

			print("TARGET: {}".format(target_uuid))

			delay_model = stat.get_delay()

			# num_samples = delay_model._n

			# print("m={}, v={}, s={}, k={}".format(delay_model._m1,
			# 	delay_model._new_variance, delay_model._skew, delay_model._kurtosis))

			# pdf = pdf_mvsk([delay_model._m1, delay_model._new_variance,
			# 		delay_model._skew, delay_model._kurtosis])

			link = peer.get_link(target_uuid)

			orig_dists = link.get_dist_params()
			print(orig_dists)

			# # Boundaries
			# xmax = max(link._all_samples)
			# xmin = min(link._all_samples)
			# xmax = xmax + float(xmax)/10
			# xmin = float(xmin)/2
			# x_plot = np.linspace(xmin, xmax, xmax-xmin)

			# # Distribution y-values
			# y_model_plot = np.array([pdf(x) for x in x_plot])
			# y_orig_plot = orig_dist.pdf(x_plot)

			# # Histogram
			# hist_y, hist_x = np.histogram(link._all_samples, bins=np.linspace(xmin, xmax,
			# 	xmax-xmin), density=True)

			# Save datasets
			#dm = ds.DistributionModelData(delay_model)
			ds.DistData(peer_uuid, target_uuid, orig_dists, delay_model,
					link._all_samples).pickle(os.path.join(ROOTDIR,
						"dist_{}_{}.pickle".format(peer_index, stat_index)))

			#print(link._historical_delta_mean)
			#print(link._historical_delta_variance)
			#print(link._historical_delta_skew)
			#print(link._historical_delta_kurtosis)
			ds.DeltaData(peer_uuid, target_uuid, link._historical_delta_uni_mean,
					link._historical_delta_uni_variance, link._historical_delta_exp_mean,
					link._historical_delta_exp_variance).pickle(os.path.join(ROOTDIR,
						"delta_{}_{}.pickle".format(peer_index, stat_index)))


			real_means = []
			real_variances = []
			real_skews = []
			real_kurtosiss = []
			for d in link._dists:
				dist = d[1]
				real_means.append((d[0], dist.get_mean()))
				real_variances.append((d[0], dist.get_variance()))
				real_skews.append((d[0], dist.get_skew()))
				real_kurtosiss.append((d[0], dist.get_kurtosis()))

			ds.ValuesData(peer_uuid, target_uuid, real_means,
					real_variances, real_skews,
					real_kurtosiss,
					link._historical_uni_mean,
					link._historical_uni_variance, link._historical_exp_mean,
					link._historical_exp_variance).pickle(os.path.join(ROOTDIR,
						"values_{}_{}.pickle".format(peer_index, stat_index)))




if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()

	parser.add_argument('--file',type=str,default=None,
		help="file with testcase defined in JSON")

	args = parser.parse_args()

	if args.file is not None:
		with open(args.file) as fd:
			json_obj = json.load(fd)

		ROOTDIR = os.path.abspath(args.file.split(".")[0])
		os.mkdir(ROOTDIR)

		DUMPDIR = os.path.join(ROOTDIR, 'dump')
		os.mkdir(DUMPDIR)

		json_file = os.path.join(ROOTDIR, 'config.json')

		with open(json_file, 'w') as outfile:
			# Save the configuration so we know the parameters
			json.dump(json_obj, outfile)

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
