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
AWG.AWG = Tektronix_AWG520(name='AWG')



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
sin_pulse_2 = pulse.CosPulse(channel='RF2', name='A sine pulse on RF')

SSB_pulse = pulse.MW_IQmod_pulse(I_channel ='RF2', Q_channel='RF1', name='SSB pulse')


# train = pulse.clock_train(channel='trigger', name='A sine pulse on RF')



sq_pulse = pulse.SquarePulse(channel='trigger',
                             name='A square pulse on MW pmod')

sq_pulse_ch1 = pulse.SquarePulse(channel='RF1',
                             name='A square pulse on MW pmod')

sq_pulse_ch2 = pulse.SquarePulse(channel='RF2',
                             name='A square pulse on MW pmod')



test_element1 = element.Element('blub_element1', pulsar = AWG)#, ignore_offset_correction=True)
test_element2 = element.Element('blub_element2', pulsar = AWG)#, ignore_offset_correction=True)

# we copied the channel definition from out global pulsar

# create a few of those
test_element1.add(pulse.cp(sq_pulse_ch2, amplitude=0.0, length=0.5e-6), start = 0.2e-6,
                 name='first pulse', refpoint='start')

test_element1.add(pulse.cp(SSB_pulse, mod_frequency=-5e6, amplitude=0.5, length=2.0e-6),
                 name='second pulse', refpulse='first pulse', refpoint='end')

test_element1.add(pulse.cp(sq_pulse, amplitude=1., length=0.5e-6), start = 0.2e-6,
                 name='third pulse', refpulse='second pulse', refpoint='end')

test_element1.add(pulse.cp(sq_pulse_ch1, amplitude=0.2, length=0.5e-6), start = 0.2e-6,
                 name='fourth pulse', refpulse='third pulse', refpoint='end')

test_element1.add(pulse.cp(sq_pulse_ch2, amplitude=0.4, length=0.5e-6), start = 0.2e-6,
                 name='fifth pulse', refpulse='fourth pulse', refpoint='end')

test_element1.add(pulse.cp(sq_pulse_ch2, amplitude=0., length=0.2e-6), start = 0.5e-6,
                 name='sixth pulse', refpulse='fifth pulse', refpoint='end')

# test_element1.add(pulse.cp(SSB_pulse, frequency=25e6, amplitude=0.3, length=1e-6),
#                  name='second pulse')

# test_element1.add(pulse.cp(sin_pulse, frequency=25e6, amplitude=0.3, length=1e-6),
#                  name='third pulse')


# test_element2.add(pulse.cp(sin_pulse, channel='RF2', frequency=1e6, amplitude=0.4, length=300e-9), start = 200e-9,
#                  name='first pulse')

# test_element2.add(pulse.LinearPulse(channel='trigger', length=1e-6,end_value = 0.9), start = 200e-9,
#                  name='second pulse')

# test_element2.add(pulse.clock_train( channel='trigger', cycles = 10,nr_down_points = 50), start = 100e-9,
#                  name='fourth pulse', refpulse='third pulse', refpoint='end',operation_type = 'RO')


test_element2.add(pulse.cp(sq_pulse_ch2, amplitude=0.0, length=0.5e-6), start = 0.2e-6,
                 name='first pulse', refpoint='start')

test_element2.add(pulse.cp(SSB_pulse, mod_frequency=-5e6, amplitude=0.5, length=2.0e-6),
                 name='second pulse', refpulse='first pulse', refpoint='end')

test_element2.add(pulse.cp(sq_pulse, amplitude=1., length=0.5e-6), start = 0.2e-6,
                 name='third pulse', refpulse='second pulse', refpoint='end')

test_element2.add(pulse.cp(sq_pulse_ch1, amplitude=0.2, length=0.5e-6), start = 0.2e-6,
                 name='fourth pulse', refpulse='third pulse', refpoint='end')

test_element2.add(pulse.cp(sq_pulse_ch2, amplitude=0.4, length=0.5e-6), start = 0.2e-6,
                 name='fifth pulse', refpulse='fourth pulse', refpoint='end')

test_element2.add(pulse.cp(sq_pulse_ch2, amplitude=0., length=0.2e-6), start = 0.5e-6,
                 name='sixth pulse', refpulse='fifth pulse', refpoint='end')



print('Channel definitions: ')

test_element1.print_overview()

test_element2.print_overview()


#-------------------------continue-------------------------------

# -------------------------------------------------------
# # viewing of the sequence for second check of timing etc
viewer.show_element_stlab(test_element1, delay = False, channels = 'all', ax = None)
viewer.show_element_stlab(test_element2, delay = False, channels = 'all', ax = None)

#--------------------------------------------------------


#-------------------------------------------------------
# now to send everything to the AWG, we have perform the last step by putting everything 
# into a sequence
seq = sequence.Sequence('blub')
seq.append(name='first_element', wfname='blub_element1', trigger_wait=True)#,
#            # goto_target='first_element')#, jump_target='first special element')

seq.append(name='second element', wfname='blub_element2', trigger_wait=True)#,
#            # goto_target='third element', jump_target='second special element')


AWG.program_awg(seq,test_element1, test_element2, verbose = True)#, test_element2)

AWG.AWGrun()


