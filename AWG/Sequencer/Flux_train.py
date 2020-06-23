import numpy as np
import time
import element
import Pulse_lib_2 as pulse
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
devAWG = Tektronix_AWG520(name='AWG', addr='TCPIP0::192.168.1.27::1234::SOCKET')
print(devAWG.get_clock())

AWG = AWG_station.AWG_Station(AWG=devAWG, ftpip='192.168.1.51')

print(AWG.clock)

AWG.define_channels(
    id='ch1',
    name='RF1',
    type='analog',
    high=0.541,
    low=-0.541,
    offset=0.,
    delay=0,
    active=True)

AWG.define_channels(
    id='ch2',
    name='RF2',
    type='analog',
    high=0.541,
    low=-0.541,
    offset=0.,
    delay=0,
    active=True)

# AWG.define_channels(
#     id='ch1_marker1',
#     name='MW_pulsemod',
#     type='marker',
#     high=1.0,
#     low=0,
#     offset=0.,
#     delay=0,
#     active=True)

AWG.define_channels(
    id='ch2_marker1',
    name='readout_trigger',
    type='marker',
    high=1,
    low=0,
    offset=0.,
    delay=0,
    active=True)  
#-------------------------------------------------------

  
sequence_name='flux_train'
SSB_modulation_frequency=250e6   
# flux_pulse_length=200e-9  
buffer_pulse_length = 1.e-5 
readout_trigger_length = 500e-9
flux_pulse_amp=0.5 
pulse_measurement_delay=500.e-9

left_reference_pulse_name = 'flux_train'

#-------------------------------------------------------
# define some bogus pulses.
# We use an element to configure and store the pulse
# For now we have defined some standard pulses but will
# increase our library in the future
sin_pulse = pulse.CosPulse(channel='RF1', name='A sine pulse on RF')
sin_pulse_2 = pulse.CosPulse(channel='RF2', name='A sine pulse on RF')

# flux_pulse = pulse.MW_IQmod_pulse(
#     I_channel='RF1', Q_channel='RF2', name='SSB pulse')

# flux_pulse = pulse.SSB_DRAG_pulse(
#     I_channel='RF1', Q_channel='RF2', name='SSB pulse')
 
flux_pulse = pulse.Filtered(
    I_channel='RF1', Q_channel='RF2', name='SSB DRAG pulse')

trigger_pulse = pulse.SquarePulse(
    channel='readout_trigger', name='A square pulse on MW pmod')
     

test_element = element.Element(
    (sequence_name + '_element'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element.add(
    pulse.cp(
        trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
    start=0.1e-6,
    name='trigger',
    refpoint='start')  

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse',
    refpulse='trigger',
    refpoint='end')


test_element.add( 
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=-flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 2',
    refpulse='flux pulse',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 3',
    refpulse='flux pulse 2',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=-flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 4',
    refpulse='flux pulse 3',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 5',
    refpulse='flux pulse 4',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=-flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 6',
    refpulse='flux pulse 5',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 7',
    refpulse='flux pulse 6',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=-flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 8',
    refpulse='flux pulse 7',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 9',
    refpulse='flux pulse 8',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=-flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 10',
    refpulse='flux pulse 9',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 11',
    refpulse='flux pulse 10',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=-flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 12',
    refpulse='flux pulse 11',
    refpoint='end')

test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 13',
    refpulse='flux pulse 12',
    refpoint='end')


test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=-flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 14',
    refpulse='flux pulse 13',
    refpoint='end')


test_element.add(
    pulse.cp(
        flux_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=flux_pulse_amp),
    start=pulse_measurement_delay,
    name='flux pulse 15',
    refpulse='flux pulse 14',
    refpoint='end')


test_element.add(
    pulse.cp(
        trigger_pulse, amplitude=0., length=buffer_pulse_length),
    start=-1 * buffer_pulse_length,
    name='buffer left',
    refpulse='trigger',
    refpoint='start')

test_element.add(  
    pulse.cp(
        trigger_pulse, amplitude=0., length=buffer_pulse_length),
    start=0,
    name='buffer right',
    refpulse='flux pulse 15',
    refpoint='end')




print('Channel definitions: ')

test_element.print_overview()


#-------------------------continue-------------------------------
# -------------------------------------------------------
# # viewing of the sequence for second check of timing etc
viewer.show_element_stlab(test_element, delay = False, channels = 'all', ax = None)

#--------------------------------------------------------


#-------------------------------------------------------
# now to send everything to the AWG, we have perform the last step by putting everything 
# into a sequence
seq = sequence.Sequence(sequence_name)
seq.append(name='first_element', wfname=sequence_name + '_element', trigger_wait=True)#,
#            # goto_target='first_element')#, jump_target='first special element')


AWG.program_awg(seq,test_element, verbose = True)#, test_element2)

AWG.AWGrun()
  

