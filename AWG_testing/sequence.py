import time
import numpy as np
import logging

class Sequence:

	"""
	Class that contains a sequence.
	A sequence is defined as a series of Elements that are given 
	certain properties, such as repetitions and jump events.

	We keep this independent of element generation here.
	Elements are simply refferec to by name, the task to ensure
	they are available lies with the AWG_station. N.B. this means that 
	Sequence.elements does not contain instances of the Element, only 
	names and meta-data.

	"""

	def __init__(self, name):
		self.name = name
	
		self.elements = []

		self.djump_table = None


	def _make_element_spec(self, name, wfname, repetitions, goto_l,
						   jump_target, trigger_wait):

		elt = {
			'name': name,
			'wfname': wfname,
			'repetitions': repetitions,
			'goto_l': goto_l,
			'jump_target': jump_target,
			'trigger_wait': trigger_wait,
			}
		return elt


	def insert_element(self, name, wfname, pos = None, repetitions=1,
					   goto_l= None, jump_target = None, trigger_wait = False,
					   **kw):

		

		for elt in self.elements:
			if elt['name'] == name:
				print('insert_element')
				print (name)
				print ('Sequence names must be unique. Not added!')
				return False

		elt = self._make_element_spec(name, wfname, repetitions, goto_l,
			jump_target, trigger_wait)


		if pos == None:
			pos = len(self.elements)
		self.elements.insert(pos,elt)

		return True


	def append(self, name, wfname, **kw):
		'''
		Takes name wfname and other arguments as input. Does not take an element as input
		'''
		self.insert_element(name, wfname, pos=len(self.elements), **kw)

	def element_count(self):
		return len(self.elements)



	def element_index(self, name, start_idx=1):
		names = [self.elements[i]['name'] for i in range(len(self.elements))]
		return names.index(name)+start_idx


	def set_djump(self, state):
		if state is True:
			# if program_sequence gets a djump_table it will set the AWG later to DJUM
			self.djump_table = {}

		if state is False:
			self.djump_table = None
		return True

	def add_djump_address(self, pattern, name):
		# name should be the name of the element and pattern the bit address
		self.djump_table[pattern] = name
		return True