# module for visualizing sequences.
#
# author: Wolfgang Pfaff

# Modified by: Sarwan Peiter

import numpy as numpy
from matplotlib import pyplot as plt

def show_element_stlab(element, delay = True, channels = 'all', ax = None):

	if ax is None:
		add_extra_labs = True
		fig, ax1 = plt.subplots(1,1, figsize = (16,8))

	else:
		# prevents extra super long legends if plots are combined
		add_extra_labs = False
	# ax1.set_axis_bgcolor('gray')
	ax2 = ax1.twinx()

	colors_dict = {'ch1': 'red',
				  'ch1_marker1': 'green',
				  'ch1_marker2': 'darkred',
				  'ch2': 'gold',
				  'ch2_marker1': 'orange',
				  'ch2_marker2': 'yellow'}

	t_vals, outputs_dict = element.waveforms()

	t_vals = t_vals * 1e9

	for key in outputs_dict:
		if 'marker' in element._channels[key]['type']:
			ax2.plot(t_vals, outputs_dict[key], label = key,
				color = colors_dict[element._channels[key]['id']])
		else:
			ax1.plot (t_vals, outputs_dict[key], label = key,
				color = colors_dict[element._channels[key]['id']])


	ax1.set_xlabel('Time (ns)')
	ax1.set_ylabel('Analog output (V)')
	if add_extra_labs:  # only set it once otherwise we end up with 20 labels
		ax2.set_ylabel('Marker output (V)')
		# ax2.legend(loc='best')

	ax1.set_xlim(t_vals.min(), t_vals.max())
	if add_extra_labs:
		ax1.legend(loc='best')

	plt.show()
	return ax1
