from __future__ import unicode_literals, absolute_import, print_function

import pickle
import os
import re
import math
from fnmatch import fnmatch

import matplotlib.pyplot as plt
import numpy as np
from statsmodels.sandbox.distributions.extras import pdf_mvsk

from tkinter import Tk, ttk, Toplevel, Menu
import tkinter as tk
import tkFont

import datasets as ds
import mock_ping as mp

class DataEntry(object):

	def __init__(self, parent_frame, grid_col, grid_row, data):

		self._data = data
		self._parent = parent_frame

		self._frame = ttk.Frame(self._parent, borderwidth=2, relief='sunken')
		self._frame.grid(column=grid_col, row=grid_row)

		self._menu = Menu(master=self._parent, tearoff=0)
		self._menu.add_command(label='info', command=self.info_popup)

		self._should_plot = tk.BooleanVar()
		self._should_plot.set(False)

		def menu_popup(event):
			self._menu.post(event.x_root, event.y_root)

		self._chkbox = ttk.Checkbutton(self._frame, text="Plot",
			variable=self._should_plot, onvalue=True)
		self._chkbox.pack()

		self._button = ttk.Button(self._frame,
			text="{} -> {}".format(grid_row, grid_col),
			command=self.info_popup
		)
		self._button.pack()

		self._button.bind('<Button-3>', menu_popup)

	@property
	def data(self):
		return self._data

	@property
	def should_plot(self):
		return self._should_plot.get()

	def info_popup(self):
		top = Toplevel()
		top.title("Info")

		frame = ttk.Frame(top)
		frame.pack()

		sourceLbl = ttk.Label(frame, text="Source")
		targetLbl = ttk.Label(frame, text="Target")

		sourceText = ttk.Label(frame, text=str(self._data._source),
			relief='sunken')
		targetText = ttk.Label(frame, text=str(self._data._target),
			relief='sunken')

		sourceLbl.grid(column=0, row=0)
		targetLbl.grid(column=1, row=0)
		sourceText.grid(column=0, row=1, padx=5, pady=5)
		targetText.grid(column=1, row=1, padx=5, pady=5)

class Plotter(object):

	def __init__(self):
		self._plot_data = []

	def add_dataplot(self, data):
		self._plot_data.append(data)

	def plot(self):
		for data in self._plot_data:
			setup_plot(data)

		plt.show()

	def clear_plots(self):
		self._plot_data = []

def get_data_files(directory):

	files = [f for f in os.listdir(directory) if fnmatch(f, "*.pickle")]

	return files

def unpickle(filepath):
	with open(filepath, 'r') as fd:
		obj = pickle.load(fd)

		# Special case since Numpy distributions can't be pickled, so the
		# arguments are pickled instead and then we recreate the object from
		# the arguments.
		if isinstance(obj, ds.DistData):
			unpacked = []
			for d in obj._original_distributions:
				#print(*d[1][1:])
				nd = mp.GammaDist(*d[1][1:])
				unpacked.append((d[0],nd))
			#print(unpacked)
			obj._original_distributions = unpacked

	return obj

def setup_plot(data):

	if isinstance(data, ds.DistData):
		setup_dist_plot(data)
	elif isinstance(data, ds.DeltaData):
		setup_delta_plot(data)
	elif isinstance(data, ds.ValuesData):
		setup_values_plot(data)

def setup_dist_plot(dist_data):
	fig = plt.figure()
	fig.suptitle("DIST: {}".format(dist_data._source))

	plt.xlabel("delay (ms)")
	plt.ylabel("probability")
	#print(dist_data._samples)

	# Boundaries and x values
	xmax = max(dist_data._samples)
	xmin = min(dist_data._samples)
	xmax = xmax + float(xmax)/10
	xmin = float(xmin)/2
	x_plot = np.linspace(xmin, xmax, xmax-xmin)

	# Histogram
	hist_y, hist_x = np.histogram(dist_data._samples, bins=np.linspace(xmin, xmax,
		xmax-xmin), density=True)

	# Plot histogram
	plt.bar(hist_x[:-1], hist_y,
		width=hist_x[1]-hist_x[0],
		color='green', alpha=0.2, linewidth=0)

	# Model distribution
	model = dist_data._distribution_model
	model_pdf = pdf_mvsk([model._m1, model._new_variance,
			model._skew, model._kurtosis])

	# Distribution y-values
	y_model_plot = np.array([model_pdf(x) for x in x_plot])

	# Distribution plots
	plt.plot(x_plot, y_model_plot, color='r',
		label='Gram-Charlier Expansion (after last iteration)')

	for i, d in enumerate(dist_data._original_distributions):
		#print("{}, {}".format(i, d))
		start_time = d[0]
		dist = d[1].get_dist()
		#print("{} {}".format(start_time, dist))
		y_plot = dist.pdf(x_plot)

		plt.plot(x_plot, y_plot,
			label='Distribution {} (start at iteration {})'.format(i, start_time))

	plt.axvline(x=dist_data._distribution_model._m1, ymin=0, ymax=1, linestyle=':',
		label='Model Mean (after last iteration)')

	plt.title("{}...".format(dist_data._target[:20]), fontdict={'fontsize':10})
	plt.legend(loc='upper right', ncol=1, fontsize=9)

	# Additional Text
	ax = fig.get_axes()
	plt.text(0.70, 0.70, "#samples={}".format(len(dist_data._samples)),
			fontsize=8, transform=ax[0].transAxes)

def setup_delta_plot(delta_data):
	fig = plt.figure()
	fig.suptitle("MV (log): {}".format(delta_data._source))

	plt.xlabel("iteration")
	plt.ylabel("delta")

	x_plot, y_plot = zip(*delta_data._delta_mean)
	plt.semilogy(x_plot, y_plot, basey=2, linestyle='-', label=r'$\Delta$mean')

	x_plot, y_plot = zip(*delta_data._delta_variance)
	plt.semilogy(x_plot, y_plot, basey=2, linestyle='-', label=r'$\Delta$variance')

	plt.title("{}...".format(delta_data._target[:20]), fontdict={'fontsize':10})
	plt.legend(loc='upper right', ncol=1, fontsize=9)

	plt.grid(True)

	fig = plt.figure()
	fig.suptitle("MV (lin): {}".format(delta_data._source))

	plt.xlabel("iteration")
	plt.ylabel("delta")

	x_plot, y_plot = zip(*delta_data._delta_mean)
	plt.plot(x_plot, y_plot, linestyle='-', label=r'$\Delta$mean')

	x_plot, y_plot = zip(*delta_data._delta_variance)
	plt.plot(x_plot, y_plot, linestyle='-', label=r'$\Delta$variance')

	plt.title("{}...".format(delta_data._target[:20]), fontdict={'fontsize':10})
	plt.legend(loc='upper right', ncol=1, fontsize=9)

	plt.grid(True)
	# fig = plt.figure()
	# fig.suptitle("SK: {}".format(delta_data._source))

	# x_plot, y_plot = zip(*delta_data._delta_skew)
	# plt.semilogy(x_plot, y_plot, basey=2, linestyle='-', label=r'$\Delta$skew')

	# x_plot, y_plot = zip(*delta_data._delta_kurtosis)
	# plt.semilogy(x_plot, y_plot, basey=2, linestyle='-', label=r'$\Delta$kurtosis')

	# plt.title("{}...".format(delta_data._target[:20]), fontdict={'fontsize':10})
	# plt.legend(loc='upper right', ncol=1, fontsize=9)

	# plt.grid(True)

def setup_values_plot(values_data):
	fig = plt.figure()
	fig.suptitle("MV: {}".format(values_data._source))

	plt.xlabel("iteration")
	plt.ylabel("value")

	x_plot, y_plot = zip(*values_data._mean_values)
	plt.plot(x_plot, y_plot, linestyle='-', label=r'mean')

	last_min = 1.0
	scale=len(x_plot)
	for i, rm in enumerate(reversed(values_data._real_means)):
		x_min = float(rm[0])/scale
		plt.axhline(y=rm[1], xmin=x_min, xmax=last_min, linestyle='-.',
			label="real mean {}".format(i))
		last_min = x_min

	x_plot, y_plot = zip(*values_data._variance_values)
	plt.plot(x_plot, y_plot, linestyle='-', label=r'variance')

	x_plot, y_plot = zip(*values_data._variance_values)
	plt.plot(x_plot, map(lambda x: math.sqrt(x), y_plot), linestyle='-', label=r'std_dev')

	last_min = 1.0
	scale=len(x_plot)
	for i, rv in enumerate(reversed(values_data._real_variances)):
		x_min = float(rv[0])/scale
		plt.axhline(y=rv[1], xmin=x_min, xmax=last_min, linestyle=':',
			label="real variance {}".format(i))
		last_min = x_min

	plt.title("{}...".format(values_data._target[:20]), fontdict={'fontsize':10})
	plt.legend(loc='upper right', ncol=1, fontsize=9)

	# Plot CofV
	fig = plt.figure()
	fig.suptitle("CofV: {}".format(values_data._source))

	plt.xlabel("iteration")
	plt.ylabel("value")

	x_plot, mean = zip(*values_data._mean_values)
	_, var = zip(*values_data._variance_values)

	y_plot = map(lambda tup: math.sqrt(tup[1])/tup[0], zip(mean, var))

	plt.plot(x_plot, y_plot, linestyle='-', label='cofv')

	#plt.plot(x_plot, map(lambda x: math.log(x), y_plot), linestyle='-', label='cofv^2')

	y_plot = map(lambda tup: tup[1]/tup[0], zip(mean, var))

	plt.plot(x_plot, y_plot, linestyle='-', label='iod')

	plt.title("{}...".format(values_data._target[:20]), fontdict={'fontsize':10})
	plt.legend(loc='upper right', ncol=1, fontsize=9)

	# fig = plt.figure()
	# fig.suptitle("SK: {}".format(values_data._source))

	# x_plot, y_plot = zip(*values_data._skew_values)
	# plt.plot(x_plot, y_plot, linestyle='-', label=r'skew')

	# for i, rs in enumerate(values_data._real_skews):
	#     plt.axhline(y=rs, xmin=0, xmax=1, linestyle='-.',
	# 	    label="real skew {}".format(i))

	# x_plot, y_plot = zip(*values_data._kurtosis_values)
	# plt.plot(x_plot, y_plot, linestyle='-', label=r'kurtosis')

	# for i, rk in enumerate(values_data._real_kurtosiss):
	#     plt.axhline(y=rk, xmin=0, xmax=1, linestyle=':',
	# 	    label="real kurtosis {}".format(i))

	# plt.title("{}...".format(values_data._target[:20]), fontdict={'fontsize':10})
	# plt.legend(loc='upper right', ncol=1, fontsize=9)

class DataExplorer(object):

	def __init__(self, directory):
		self._plotter = Plotter()
		self._data_entries = []

		self._root = Tk()
		self._root.title("Data Explorer")

		self._font = tkFont.Font(root=self._root,family="Helvetica",size=10)
		self._style = ttk.Style()
		self._style.configure('.', font=self._font)

		self._content_frame = ttk.Frame(self._root, width=300)
		self._content_frame.pack()

		# DATA FRAME
		self._data_frame = ttk.Frame(self._content_frame)
		self._data_frame.grid(row=0)

		self._dist_label = ttk.Label(self._data_frame, text='Distributions')
		self._delta_label = ttk.Label(self._data_frame, text='Deltas')
		self._values_label = ttk.Label(self._data_frame, text='Values')

		self._dist_label.grid(column=0, row=0, pady=5)
		self._delta_label.grid(column=1, row=0, pady=5)
		self._values_label.grid(column=2, row=0, pady=5)

		self._dist_frame = ttk.Frame(self._data_frame, borderwidth=5, relief='raised')
		self._dist_frame.grid(column=0, row=1, padx=5)

		self._delta_frame = ttk.Frame(self._data_frame, borderwidth=5, relief='raised')
		self._delta_frame.grid(column=1, row=1, padx=5)

		self._values_frame = ttk.Frame(self._data_frame, borderwidth=5, relief='raised')
		self._values_frame.grid(column=2, row=1, padx=5)

		# CONTROL FRAME
		self._control_frame = ttk.Frame(self._content_frame)
		self._control_frame.grid(row=1, pady=5, padx=5, sticky=(tk.W))

		# LEGEND FRAME
		self._legend_frame = ttk.Frame(self._content_frame)
		self._legend_frame.grid(row=2, pady=5, padx=5)
		legend_labels = {}

		# Set up data
		files = get_data_files(directory)

		for i, f in enumerate(files):
			filepath = os.path.join(directory, f)

			m = re.search('.*(\d+)_(\d+)\.pickle', f)
			# From
			grid_row = int(m.group(1))
			# To
			grid_col = int(m.group(2))

			data_object = unpickle(filepath)

			if grid_row not in legend_labels:
				legend_labels[grid_row] = ttk.Label(self._legend_frame,
					text="{}: {}".format(grid_row, str(data_object._source)))

			if isinstance(data_object, ds.DistData):
				master_frame = self._dist_frame
			elif isinstance(data_object, ds.DeltaData):
				master_frame = self._delta_frame
			elif isinstance(data_object, ds.ValuesData):
				master_frame = self._values_frame

			de = DataEntry(master_frame, grid_col, grid_row, data_object)

			self._data_entries.append(de)

		# Set up control buttons
		plot_button = ttk.Button(self._control_frame,
			text="Plot selected",
			command=self._plot_selected
		)
		plot_button.grid()

		# Set up legend
		legend_head = ttk.Label(self._legend_frame, text="Legend")
		legend_head.grid(row=0, column=0, sticky=(tk.N, tk.W))

		for i, ll in legend_labels.iteritems():
			ll.grid(row=i+1, column=0, sticky=(tk.N, tk.W))

	def _plot_selected(self):
		for de in self._data_entries:
			if de.should_plot:
				self._plotter.add_dataplot(de.data)

		self._plotter.plot()
		self._plotter.clear_plots()

	def start(self):
		self._root.mainloop()

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()

	parser.add_argument('--dir', type=str,
		help="The directory where the data is located.")

	args = parser.parse_args()

	if args.dir is not None:
		directory = os.path.abspath(args.dir)
		de = DataExplorer(directory)
		de.start()
	else:
		print("No directory specified.")
