import numpy as np
import time
import element
import Pulse_lib as pulse
import AWG_station
import sequence
import pprint
import imp
import viewer
from AWG520_driver_beta import Tektronix_AWG520
from matplotlib import pyplot as plt

imp.reload(pulse)
imp.reload(element)
imp.reload(AWG_station)
imp.reload(viewer)

plt.close('all')

#------------------------------------------------------
# Define all the channels on AWG through AWG_station.
# This then again uses the low level AWG driver to communicate with the AWG instrument
# So one never uses the low level AWG driver directly but instead through an interface 
AWG = AWG_station.AWG_Station()
# AWG.AWG = Tektronix_AWG520(name='AWG')


AWG.define_channels(id='ch1', name='RF1', type='analog',
                              high=0.541, low=-0.541,
                              offset=0., delay=0, active=True)

AWG.define_channels(id='ch2', name='RF2', type='analog',
                              high=0.541, low=-0.541,
                              offset=0., delay=0, active=True)

AWG.define_channels(id='ch1_marker1', name='MW_pulsemod', type='marker',
                              high=1.0, low=0, offset=0.,
                              delay=0, active=True)

AWG.define_channels(id='ch2_marker1', name='trigger', type='marker',
                              high=1, low=0,
                              offset=0., delay=0, active=True)
#-------------------------------------------------------


#-------------------------------------------------------
# define some bogus pulses.
# We use an element to configure and store the pulse
# For now we have defined some standard pulses but will
# increase our library in the future
sin_pulse = pulse.CosPulse(channel='RF1', name='A sine pulse on RF')

# train = pulse.clock_train(channel='trigger', name='A sine pulse on RF')



sq_pulse = pulse.SquarePulse(channel='MW_pulsemod',
                             name='A square pulse on MW pmod')



test_element1 = element.Element('a_test_element1', pulsar = AWG)#, ignore_offset_correction=True)
test_element2 = element.Element('a_test_element2', pulsar = AWG)#, ignore_offset_correction=True)

# we copied the channel definition from out global pulsar

# create a few of those
test_element1.add(pulse.cp(sin_pulse, frequency=100e6, amplitude=0.3, length=0.3e-6),
                 name='first pulse')
test_element1.add(pulse.cp(sq_pulse, amplitude=1, length=0.5e-6), start = 0.2e-6,
                 name='second pulse', refpulse='first pulse', refpoint='end',operation_type = 'RO')

test_element2.add(pulse.cp(sin_pulse, channel='RF2', frequency=2e6, amplitude=0.2, length=1e-6), start = 200e-9,
                 name='third pulse')

test_element2.add(pulse.clock_train( channel='trigger', cycles = 10,nr_down_points = 50), start = 100e-9,
                 name='fourth pulse', refpulse='third pulse', refpoint='end',operation_type = 'RO')


print('Channel definitions: ')

test_element1.print_overview()

test_element2.print_overview()

#-------------------------continue-------------------------------

# -------------------------------------------------------
# viewing of the sequence for second check of timing etc
viewer.show_element_stlab(test_element1, delay = False, channels = 'all', ax = None)
viewer.show_element_stlab(test_element2, delay = False, channels = 'all', ax = None)

#--------------------------------------------------------


#-------------------------------------------------------
# now to send everything to the AWG, we have perform the last step by putting everything 
# into a sequence

seq = sequence.Sequence('A Sequence')
seq.append(name='first_element', wfname='a_test_element1', trigger_wait=True)#,
           # goto_target='first_element')#, jump_target='first special element')

seq.append('second element', 'a_test_element2', trigger_wait=True, repetitions=5)#,
           # goto_target='third element', jump_target='second special element')


AWG.program_awg(seq,test_element1, test_element2, verbose = True)#, test_element2)


