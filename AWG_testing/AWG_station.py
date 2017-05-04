"""
So I have already written the driver for the AWG. 
Now the next step is to write an interface to communicates with driver.
An also usefull interface is to write a library to generate pulses.

"""
import time
import logging
import numpy as np
import struct
import os

# some pulses use rounding when determining the correct sample at which to
# insert a particular value. this might require correct rounding -- the pulses
# are typically specified on short time scales, but the time unit we use is
# seconds. therefore we need a suitably chosen digit on which to round. 9 would
# round a pulse to 1 ns precision. 11 is 10 ps, and therefore probably beyond
# the lifetime of this code (no 10ps AWG available yet :))
SIGNIFICANT_DIGITS = 11


# Make a station which represents your instruments and define all the channels
# of the instrument and connections between them

# TODO: function which sets up AWG configuration
# modified by Sarwan Peiter

class AWG_Station():

	"""
	This object communicates with the AWG520 series
	"""
	AWG = None
	AWG_type = 'regular'
	clock = 1e9
	channels_ids =  ['ch1', 'ch1_marker1', 'ch1_marker2',
					'ch2', 'ch2_marker1', 'ch2_marker2']

	AWG_sequence_cfg = {}

	def __init__(self):

		self.channels = {}



	# define channels to for connection to environment
	
	def define_channels(self, id, name, type, delay, offset, high, low, active):

		_doubles = []
		# Check whether or not channels are already in use!
		for c in self.channels:
			if self.channels[c]['id'] == id:
				logging.warning(
					"Channel '%s' already in use, will overwrite." % id)
				_doubles.append(c)
		for c in _doubles:
			del self.channels[c]

		self.channels[name] = {'id': id,
							   'type': type,
							   'delay': delay,
							   'offset': offset,
							   'high': high,
							   'low': low,
							   'active': active}



	# Get the channels names by id 
	def get_channel_names_by_id(self, id):
		chans = {id: None, id+'_marker1': None, id+'_marker2': None}
		for c in self.channels:
			if self.channels[c]['id'] in chans:
				chans[self.channels[c]['id']] = c
		return chans



	def get_channel_name_by_id(self, id):
		for c in self.channels:
			if self.channels[c]['id'] == id:
				return c

	def get_used_channel_ids(self):
		chans = []
		for c in self.channels:
			if self.channels[c]['active'] and \
					self.channels[c]['id'][:3] not in chans:
				chans.append(self.channels[c]['id'][:3])
		return chans
		

	# Make function which programs AWG

	def get_awg_channel_cfg(self):
		channel_cfg = {}

		self.AWG.get_all()



	def delete_all_waveforms(self):
		self.AWG.clear_waveforms()
		

	def program_awg(self, sequence,*elements,**kw):

		"""
		Upload a single file to the AWG (.awg) which contains all waveforms
		AND sequence information (i.e. nr of repetitions, event jumps etc)
		Advantage is that it's much faster, since sequence information is sent
		to the AWG in a single file.
		"""

		self.last_sequence = sequence
		self.last_elements = elements

		# making directory to store waveforms and sequences
		self.init_dir()

		# old_timeout = self.AWG.timeout() # whats this function
		# self.AWG.timeout(max(180, old_timeout))

		verbose = kw.pop('verbose', False)
		debug = kw.pop('debug', False)
		channels = kw.pop('channels', 'all')
		loop = kw.pop('loop', False)
		allow_non_zero_first_point_on_trigger_wait = kw.pop('allow_first_zero', False)
		elt_cnt = len(elements)
		chan_ids = self.get_used_channel_ids()

		packed_waveforms = {}
		# Store offset settings to restore them after upload the seq
		# Note that this is the AWG setting offset, as distinct from the
		# channel parameter offset.

		elements_with_non_zero_first_points = []


		# order the waveforms according to physical AWG channels and
		# make empty sequences where necessary


		for i, element in enumerate(elements):
			if verbose:
				print ("%d / %d: %s (%d samples)... " %\
					(i+1, elt_cnt, element.name, element.samples()), end = ' ')

			_t0 = time.time()

			tvals, wfs = element.normalized_waveforms()

			for id in chan_ids:
				wfname = element.name + '_%s' % id



				chan_wfs = {id: None, id+'_marker1': None, id+'_marker2': None}

				grp = self.get_channel_names_by_id(id)
				
				for sid in grp:
					if grp[sid] != None and grp[sid] in wfs:
						chan_wfs[sid] = wfs[grp[sid]]
						if chan_wfs[sid][0] != 0.:
							elements_with_non_zero_first_points.append(element.name)


					else:
						chan_wfs[sid] = np.zeros(element.samples())


				# create wform files and send them to AWG
				packed_waveforms[wfname] = self.AWG.gen_waveform_files(chan_wfs[id],
											chan_wfs[id+'_marker1'],
											chan_wfs[id+'_marker2'], wfname, 
											int(element.clock))

				# self.AWG.send_waveform
		_t = time.time() - _t0

		if verbose:
			print ("finished in %.2f seconds." % _t)


		# sequence programming

		_t0 = time.time()

		if (sequence.element_count() > 8000):

			logging.warning("Error: trying to program '{:s}' ({:d}'".format(
							sequence.name, sequence.element_count()) +
							" element(s))...\n Sequence contains more than " +
							"8000 elements, Aborting", end=' ')

			return


		print("Programming '%s' (%d element(s)) \t"
			  % (sequence.name, sequence.element_count()), end=' ')


		# determine which channels are involved in the sequence
		if channels == 'all':
			chan_ids = self.get_used_channel_ids()

		else:
			chan_ids = []
			for c in channels:
				if self.channels[c]['id'][:3] not in chan_ids:
					chan_ids.append(self.channels[c]['id'][:3])


		# Create lists with sequence information:
		# wfname_l = list of waveform names [[wf1_ch1,wf2_ch1..],[wf1_ch2,wf2_ch2..],...]
		# nrep_l = list specifying the number of reps for each seq element
		# wait_l = idem for wait_trigger_state
		# goto_l = idem for goto_state (goto is the element where it hops to in case the element is finished)


		wfname_l = []
		nrep_l = []
		wait_l = []
		goto_l = []
		logic_jump_l = []

		for id in chan_ids:
			#set all the waveforms

			el_wfnames = []

			# add all wf names of channel

			for elt in sequence.elements:
				el_wfnames.append(elt['wfname'] + '_%s' % id)
				# should the name include id nr?

			wfname_l.append(el_wfnames)


		for elt in sequence.elements:
			nrep_l.append(elt['repetitions'])
			if (elt['repetitions'] < 1) or (elt['repetitions'] > 65536):
				raise Exception('pulsar: The number of repetitions of ' +
								'AWG element "%s" are out of range. Valid '
								% elt['wfname'] +
								'range = 1 to 65536 ("%s" recieved)'
								% elt['repetitions'])

			if elt['goto_l'] != None:
				goto_l.append(sequence.element_index(elt['goto_l']))
			else:
				goto_l.append(0)
			if elt['jump_target'] != None:
				logic_jump_l.append(sequence.element_index(elt['jump_target']))
			else:
				logic_jump_l.append(0)
			if elt['trigger_wait']:
				wait_l.append(1)
			   
			else:
				wait_l.append(0)

		if loop:
			goto_l[-1] = 1
	  
		# setting jump modes and loading the djump table
		if sequence.djump_table != None and self.AWG_type not in ['opt09']:
			raise Exception('pulsar: The AWG configured does not support dynamic jumping')

		if self.AWG_type in ['opt09']:
			# TODO as self.AWG_sequence_cfg no longer exists but is generated
			# from the sequence_cfg file, make these set the values on the AWG
			# itself.
			if sequence.djump_table != None:
				# self.AWG_sequence_cfg['EVENT_JUMP_MODE'] = 2  # DYNAMIC JUMP
				print('AWG set to dynamical jump')
				awg_djump_table = np.zeros(16, dtype='l')
				for i in list(sequence.djump_table.keys()):
					el_idx = sequence.element_index(sequence.djump_table[i])
					awg_djump_table[i] = el_idx
				# self.AWG_sequence_cfg['TABLE_JUMP_DEFINITION'] = awg_djump_table

			else:
				# self.AWG_sequence_cfg['EVENT_JUMP_MODE'] = 1  # EVENT JUMP
			   pass

		if debug:
			self.check_sequence_consistency(packed_waveforms,
											wfname_l,
											nrep_l, wait_l, goto_l,
											logic_jump_l)

		filename = sequence.name+'_FILE.seq'
		

		# # Loading the sequence onto the AWG memory
		self.AWG.gen_sequence_files(wfname_l[0],wfname_l[1],nrep_l,wait_l,goto_l,logic_jump_l,filename)

		time.sleep(.1)
		# # # Waits for AWG to be ready
		self.AWG.is_awg_ready()

		_t = time.time() - _t0
		print(" finished in %.2f seconds." % _t)

		return 0





	def check_sequence_consistency(self, packed_waveforms,
								   wfname_l,
								   nrep_l, wait_l, goto_l, logic_jump_l):
		'''
		Specific for 2 channel tektronix 520 where all channels are used.
		'''
		if not (len(wfname_l[0]) == len(wfname_l[1]) ==
				len(nrep_l) == len(wait_l) == len(goto_l) ==
				len(logic_jump_l)):
			raise Exception('pulsar: sequence list of elements/properties has unequal length')
	  
	# def test_send(self,w,m1,m2,filename,clock):
	# 	"""
	# 	Sends a complete waveform. All parameters need to be specified.
	# 	choose a file extension 'wfm' (must end with .pat)
	# 	See also: resend_waveform()
	# 	Input:
	# 		w (float[numpoints]) : waveform
	# 		m1 (int[numpoints])  : marker1
	# 		m2 (int[numpoints])  : marker2
	# 		filename (string)    : filename
	# 		clock (int)          : frequency (Hz)
	# 	Output:
	# 		None
	# 	"""
	# 	logging.debug(__name__ + ' : Generating wfm files %s for instrument' % filename)

	# 	# Check for errors
	# 	dim = len(w)

	# 	if (not((len(w)==len(m1)) and ((len(m1)==len(m2))))):
	# 		return 'error'
		

	# 	m = m1 + np.multiply(m2,2)
	# 	ws = b''
	# 	for i in range(0,len(w)):
	# 		ws = ws + struct.pack('<fB', w[i], int(m[i]))


	# 	s1 = 'MAGIC 1000\r\n'
	# 	s3 = ws
	# 	s4 = 'CLOCK %.10e\r\n' % clock

	# 	s2 = '#' + str(len(str(len(s3)))) + str(len(s3))
		
	

	# 	mes =  s1.encode('ASCII')  + s2.encode('ASCII') + s3 + s4.encode('ASCII')

	# 	with open(os.path.join(self.dir, filename), 'wb') as d:
	# 		d.write(mes)
	# 		d.close()
		

	# def test_send_sequence2(self,wfs1,wfs2,rep,wait,goto,logic_jump,filename):
	# 	'''
	# 	Sends a sequence file
	# 	Inputs (mandatory):
	# 		wfs1:  list of filenames for ch1 (all must end with .pat)
	# 		wfs2: list of filenames for ch2 (all must end with .pat)
	# 		rep: list
	# 		wait: list
	# 		goto: list
	# 		logic_jump: list
	# 		filename: name of output file (must end with .seq)
	# 	Output:
	# 		None
	# 	'''
	# 	logging.debug(__name__ + ' : Generating sequence %s for instrument' % filename)


	# 	N = str(len(rep))
	
	# 	s1 = 'MAGIC 3002\r\n'
	# 	s3 = 'LINES %s\n'%N
	# 	s4 = ''


	# 	for k in range(len(rep)):
	# 		s4 = s4+ '"%s","%s",%s,%s,%s,%s\r\n'%(wfs1[k],wfs2[k],rep[k],wait[k],goto[k],logic_jump[k])



	# 	mes = s1.encode("ASCII")  + s3.encode("ASCII")+ s4.encode("ASCII")
	# 	with open(os.path.join(self.dir, filename), 'wb') as d:
	# 		d.write(mes)
	# 		d.close()