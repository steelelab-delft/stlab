# Written by Sarwan Peiter


import time 
import logging
from stlab.AWG_testing.RS_FSV_beta import RS_RFS


class FSV_station(RS_FSV):


	def __init__(self):
		self.FSV = None
		super(FSV_station, self).__init__()
		
	def prepare(self):

		# Preparing readout instrument FSV
		self.set_IQ_mode()
		self.set_clock_ext()
		self.set_trigger_ext()
		self.set_pre_amp('on')
		self.set_50_inp_imp()
		self.sel_rf_inp()
		self.set_sweep_time(tsweep= 1.5e-6)
		
	def measure(self):
		self.start()

	def get_values(self):
		self.get_trace_data()