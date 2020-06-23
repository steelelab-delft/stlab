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
devAWG = Tektronix_AWG520(name='AWG',addr='TCPIP0::192.168.1.27::1234::SOCKET')
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

AWG.define_channels(
    id='ch2_marker1',
    name='MW_pulsemod',
    type='marker',
    high=1.0,
    low=0,
    offset=0.,
    delay=0,
    active=True)  

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

sequence_name='T2_delay_scan'
measurement_trigger_delay=500e-9
SSB_modulation_frequency=-50e6
measurement_pulse_length=500e-9
pulse_length=60e-9
pulse_measurement_delay=-300e-9
buffer_pulse_length = 1.e-6
readout_trigger_length = 500e-9  
pulse_amp=0.5
time_delay=150e-9


# left_reference_pulse_name = 'pulsed spec'

#--------------------------------------------------------



gaussian_SSB_pulse = pulse.SSB_DRAG_pulse(
    I_channel='RF1', Q_channel='RF2', name='SSB DRAG pulse')

readout_switch_marker = pulse.SquarePulse(
    channel='MW_pulsemod', name='A square pulse on MW pmod')

ATS_trigger_pulse = pulse.SquarePulse(
    channel='readout_trigger', name='A square pulse on MW pmod')

test_element0 = element.Element(
    (sequence_name + '_element0'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element1 = element.Element(
    (sequence_name + '_element1'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element2 = element.Element(
    (sequence_name + '_element2'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element3 = element.Element(
    (sequence_name + '_element3'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element4 = element.Element(
    (sequence_name + '_element4'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element5 = element.Element(
    (sequence_name + '_element5'),
    pulsar=AWG)  #, ignore_offset_correction=True)


element_list=[test_element0, test_element1,test_element2,test_element3,test_element4,test_element5]

#element0

element_list[0].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
        start=0.1e-6, 
        name='readout trigger',
        refpoint='start')

element_list[0].add(
    pulse.cp(readout_switch_marker, amplitude=1., length=measurement_pulse_length),
    start=measurement_trigger_delay,
    name='readout switch marker',
    refpulse='readout trigger',
    refpoint='start')

element_list[0].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='readout trigger',
        refpoint='start')

element_list[0].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout switch marker',
        refpoint='end')

#element1

element_list[1].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
        start=0.1e-6, 
        name='readout trigger',
        refpoint='start')

element_list[1].add(
    pulse.cp(readout_switch_marker, amplitude=1., length=measurement_pulse_length),
    start=measurement_trigger_delay,
    name='readout switch marker',
    refpulse='readout trigger',
    refpoint='start')


element_list[1].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=-pulse_measurement_delay - pulse_length,
        name='qubit drive pulse',
        refpulse='readout trigger',
        refpoint='start')


element_list[1].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='qubit drive pulse',
        refpoint='start')

element_list[1].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout switch marker',
        refpoint='end')

#element2


element_list[2].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
        start=0.1e-6, 
        name='readout trigger',
        refpoint='start')

element_list[2].add(
    pulse.cp(readout_switch_marker, amplitude=1., length=measurement_pulse_length),
    start=measurement_trigger_delay,
    name='readout switch marker',
    refpulse='readout trigger',
    refpoint='start')


element_list[2].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=-pulse_measurement_delay - pulse_length,
        name='qubit drive pulse',
        refpulse='readout trigger',
        refpoint='start')

element_list[2].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=- time_delay,
        name='qubit drive pulse 2',
        refpulse='qubit drive pulse',
        refpoint='start')


element_list[2].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='qubit drive pulse 2',
        refpoint='start')

element_list[2].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout switch marker',
        refpoint='end')

#element3


element_list[3].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
        start=0.1e-6, 
        name='readout trigger',
        refpoint='start')

element_list[3].add(
    pulse.cp(readout_switch_marker, amplitude=1., length=measurement_pulse_length),
    start=measurement_trigger_delay,
    name='readout switch marker',
    refpulse='readout trigger',
    refpoint='start')


element_list[3].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=-pulse_measurement_delay - pulse_length,
        name='qubit drive pulse',
        refpulse='readout trigger',
        refpoint='start')

element_list[3].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=- time_delay,
        name='qubit drive pulse 2',
        refpulse='qubit drive pulse',
        refpoint='start')

element_list[3].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start= - time_delay,
        name='qubit drive pulse 3',
        refpulse='qubit drive pulse 2',
        refpoint='start')

element_list[3].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='qubit drive pulse 3',
        refpoint='start')


element_list[3].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout switch marker',
        refpoint='end')

#element4


element_list[4].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
        start=0.1e-6, 
        name='readout trigger',
        refpoint='start')

element_list[4].add(
    pulse.cp(readout_switch_marker, amplitude=1., length=measurement_pulse_length),
    start=measurement_trigger_delay,
    name='readout switch marker',
    refpulse='readout trigger',
    refpoint='start')


element_list[4].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=-pulse_measurement_delay - pulse_length,
        name='qubit drive pulse',
        refpulse='readout trigger',
        refpoint='start')

element_list[4].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=- time_delay,
        name='qubit drive pulse 2',
        refpulse='qubit drive pulse',
        refpoint='start')

element_list[4].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start= - time_delay,
        name='qubit drive pulse 3',
        refpulse='qubit drive pulse 2',
        refpoint='start')

element_list[4].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start= - time_delay,
        name='qubit drive pulse 4',
        refpulse='qubit drive pulse 3',
        refpoint='start')

element_list[4].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='qubit drive pulse 4',
        refpoint='start')


element_list[4].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout switch marker',
        refpoint='end')


#element5


element_list[5].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=1.,
        length=readout_trigger_length),
        start=0.1e-6, 
        name='readout trigger',
        refpoint='start')

element_list[5].add(
    pulse.cp(readout_switch_marker, amplitude=1., length=measurement_pulse_length),
    start=measurement_trigger_delay,
    name='readout switch marker',
    refpulse='readout trigger',
    refpoint='start')


element_list[5].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=-pulse_measurement_delay - pulse_length,
        name='qubit drive pulse',
        refpulse='readout trigger',
        refpoint='start')

element_list[5].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start=- time_delay,
        name='qubit drive pulse 2',
        refpulse='qubit drive pulse',
        refpoint='start')

element_list[5].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start= - time_delay,
        name='qubit drive pulse 3',
        refpulse='qubit drive pulse 2',
        refpoint='start')

element_list[5].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start= - time_delay,
        name='qubit drive pulse 4',
        refpulse='qubit drive pulse 3',
        refpoint='start')

element_list[5].add(
    pulse.cp(
        gaussian_SSB_pulse,
        mod_frequency=SSB_modulation_frequency,
        amplitude=pulse_amp,
        sigma=pulse_length,
        nr_sigma=2,
        motzoi=0),
        start= - time_delay,
        name='qubit drive pulse 5',
        refpulse='qubit drive pulse 4',
        refpoint='start')

element_list[5].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='qubit drive pulse 5',
        refpoint='start')


element_list[5].add(
    pulse.cp(
        ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout switch marker ',
        refpoint='end')

print('Channel definitions: ')
for i in range(len(element_list)):
    element_list[i].print_overview()

  

#-------------------------continue------------ -------------------
# -------------------------------------------------------
# # viewing of the sequence for second check of timing etc
for i in range(len(element_list)):
    viewer.show_element_stlab(element_list[i], delay = False, channels = 'all', ax = None)

#--------------------------------------------------------


#-------------------------------------------------------
# now to send everything to the AWG, we have perform the last step by putting everything 
# into a sequence
seq = sequence.Sequence(sequence_name)

seq.append(name='zeroth_element', wfname=sequence_name + '_element0', trigger_wait=True)

seq.append(name='first_element', wfname=sequence_name + '_element1', trigger_wait=True)#,
#            # goto_target='first_element')#, jump_target='first special element')
seq.append(name='second element', wfname=sequence_name + '_element2', trigger_wait=True)#,
#            # goto_target='third element', jump_target='second special element')
seq.append(name='third element', wfname=sequence_name + '_element3', trigger_wait=True)#,

seq.append(name='4th element', wfname=sequence_name + '_element4', trigger_wait=True)#,

seq.append(name='5th element', wfname=sequence_name + '_element5', trigger_wait=True)#,


AWG.program_awg(seq,test_element0,test_element1,test_element2,test_element3,test_element1,test_element2,test_element3,test_element4,test_element5,
verbose = True)#, test_element2)

AWG.AWGrun()