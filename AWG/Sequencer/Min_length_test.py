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

print(AWG_station.__file__)

imp.reload(pulse)
imp.reload(element)
imp.reload(AWG_station)
imp.reload(viewer)

plt.close('all')

#------------------------------------------------------
# Define all the channels on AWG through AWG_station.
# This then again uses the low level AWG driver to communicate with the AWG instrument
# So one never uses the low level AWG driver directly but instead through an interface 
devAWG = Tektronix_AWG520(name='AWG', addr='TCPIP0::192.168.1.28::4000::SOCKET')
print(devAWG.get_clock())

AWG = AWG_station.AWG_Station(AWG=devAWG, ftpip='192.168.1.28')

print(AWG.clock)

# AWG.define_channels(
#     id='ch1',
#     name='RF1',
#     type='analog',
#     high=0.541,
#     low=-0.541,
#     offset=0.,
#     delay=0,
#     active=True)

# AWG.define_channels(
#     id='ch2',
#     name='RF2',
#     type='analog',
#     high=0.541,
#     low=-0.541,
#     offset=0.,
#     delay=0,
#     active=True)

# AWG.define_channels(
#     id='ch2_marker1',
#     name='MW_pulsemod',
#     type='marker',
#     high=1.0,
#     low=0,
#     offset=0.,
#     delay=0,
#     active=True)

AWG.define_channels(
    id='ch1_marker1',
    name='readout_trigger',
    type='marker',
    high=1,
    low=0,
    offset=0.,
    delay=0,
    active=True)  
#-------------------------------------------------------

  
sequence_name='min'
readout_trigger_length = 1201e-9  
spec_pulse_amp=0.3


#-------------------------------------------------------
# define some bogus pulses.
# We use an element to configure and store the pulse
# For now we have defined some standard pulses but will
# increase our library in the future
sin_pulse = pulse.CosPulse(channel='RF1', name='A sine pulse on RF')
sin_pulse_2 = pulse.CosPulse(channel='RF2', name='A sine pulse on RF')

qubit_spec_SSB_pulse = pulse.MW_IQmod_pulse(
    I_channel='RF1', Q_channel='RF2', name='SSB pulse')

ATS_trigger_pulse = pulse.SquarePulse(
    channel='readout_trigger', name='A square pulse on MW pmod')
   

test_element1 = element.Element(
    (sequence_name + '_element1'),
    pulsar=AWG)  #, ignore_offset_correction=True)
test_element2 = element.Element(
    (sequence_name + '_element2'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element1.add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
    start=0.0e-6,
    name='readout trigger',
    refpoint='start')  


#### Element 2 is identical to element 1

test_element2.add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
    start=0.0e-6,
    name='readout trigger',
    refpoint='start')


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
seq = sequence.Sequence(sequence_name)
seq.append(name='first_element', wfname=sequence_name + '_element1', trigger_wait=True)#,
# #            # goto_target='first_element')#, jump_target='first special element')
# seq.append(name='second element', wfname=sequence_name + '_element2', trigger_wait=True)#,
# #            # goto_target='third element', jump_target='second special element')


AWG.program_awg(seq,test_element1,test_element2, verbose = True)#, test_element2)

AWG.AWGrun()
  

