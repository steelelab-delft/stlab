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

sequence_name='T1_delay_scan'
measurement_trigger_delay=500e-9
SSB_modulation_frequency=50e6
measurement_pulse_length=500e-9
pulse_sigma=15e-9
pulse_measurement_delay=-500e-9
buffer_pulse_length = 1.e-6
readout_trigger_length = 500e-9  
pulse_amp=0.5
time_delay=np.arange(400e-9,8.6e-6,400e-9)


# left_reference_pulse_name = 'pulsed spec'

#--------------------------------------------------------



gaussian_SSB_pulse = pulse.SSB_DRAG_pulse(
    I_channel='RF1', Q_channel='RF2', name='SSB DRAG pulse')

readout_switch_marker = pulse.SquarePulse(
    channel='MW_pulsemod', name='A square pulse on MW pmod')

ATS_trigger_pulse = pulse.SquarePulse(
    channel='readout_trigger', name='A square pulse on MW pmod')


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

test_element6 = element.Element(
    (sequence_name + '_element6'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element7 = element.Element(
    (sequence_name + '_element7'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element8 = element.Element(
    (sequence_name + '_element8'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element9 = element.Element(
    (sequence_name + '_element9'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element10 = element.Element(
    (sequence_name + '_element10'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element11 = element.Element(
    (sequence_name + '_element11'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element12 = element.Element(
    (sequence_name + '_element12'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element13 = element.Element(
    (sequence_name + '_element13'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element14 = element.Element(
    (sequence_name + '_element14'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element15 = element.Element(
    (sequence_name + '_element15'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element16 = element.Element(
    (sequence_name + '_element16'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element17 = element.Element(
    (sequence_name + '_element17'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element18 = element.Element(
    (sequence_name + '_element18'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element19 = element.Element(
    (sequence_name + '_element19'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element20 = element.Element(
    (sequence_name + '_element20'),
    pulsar=AWG)  #, ignore_offset_correction=True)

test_element21 = element.Element(
    (sequence_name + '_element21'),
    pulsar=AWG)  #, ignore_offset_correction=True)

element_list=[test_element1,test_element2,test_element3,test_element4,test_element5,
test_element6,test_element7,test_element8,test_element9,test_element10,test_element11,
test_element12,test_element13,test_element14,test_element15,test_element16,test_element17,
test_element18,test_element19,test_element20,test_element21]

for i in range(len(time_delay)):
    element_list[i].add(
        pulse.cp(
            ATS_trigger_pulse, amplitude=1.,
            length=readout_trigger_length),
        start=0.1e-6, 
        name='readout trigger',
        refpoint='start')

    element_list[i].add(
        pulse.cp(readout_switch_marker, amplitude=1., length=measurement_pulse_length),
        start=measurement_trigger_delay,
        name='readout switch marker',
        refpulse='readout trigger',
        refpoint='start')


    element_list[i].add(
        pulse.cp(
            gaussian_SSB_pulse,
            mod_frequency=SSB_modulation_frequency,
            amplitude=pulse_amp,
            sigma=pulse_sigma,
            nr_sigma=4,
            motzoi=0),
        start=-pulse_measurement_delay - pulse_sigma*4 - time_delay[i],
        name='qubit drive pulse',
        refpulse='readout trigger',
        refpoint='start')


    element_list[i].add(
        pulse.cp(
            ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='qubit drive pulse',
        refpoint='start')

    element_list[i].add(
        pulse.cp(
            ATS_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout switch marker',
        refpoint='end')



print('Channel definitions: ')
for i in range(len(time_delay)):
    element_list[i].print_overview()



#-------------------------continue------------ -------------------
# -------------------------------------------------------
# # viewing of the sequence for second check of timing etc
for i in range(len(time_delay)):
    viewer.show_element_stlab(element_list[i], delay = False, channels = 'all', ax = None)

#--------------------------------------------------------


#-------------------------------------------------------
# now to send everything to the AWG, we have perform the last step by putting everything 
# into a sequence
seq = sequence.Sequence(sequence_name)
seq.append(name='first_element', wfname=sequence_name + '_element1', trigger_wait=True)#,
#            # goto_target='first_element')#, jump_target='first special element')
seq.append(name='second element', wfname=sequence_name + '_element2', trigger_wait=True)#,
#            # goto_target='third element', jump_target='second special element')
seq.append(name='third element', wfname=sequence_name + '_element3', trigger_wait=True)#,

seq.append(name='4th element', wfname=sequence_name + '_element4', trigger_wait=True)#,

seq.append(name='5th element', wfname=sequence_name + '_element5', trigger_wait=True)#,

seq.append(name='6th element', wfname=sequence_name + '_element6', trigger_wait=True)#,

seq.append(name='7th element', wfname=sequence_name + '_element7', trigger_wait=True)#,

seq.append(name='8th element', wfname=sequence_name + '_element8', trigger_wait=True)#,

seq.append(name='9th element', wfname=sequence_name + '_element9', trigger_wait=True)#,

seq.append(name='10th element', wfname=sequence_name + '_element10', trigger_wait=True)#,

seq.append(name='11th element', wfname=sequence_name + '_element11', trigger_wait=True)#,

seq.append(name='12th element', wfname=sequence_name + '_element12', trigger_wait=True)#,

seq.append(name='13th element', wfname=sequence_name + '_element13', trigger_wait=True)#,

seq.append(name='14th element', wfname=sequence_name + '_element14', trigger_wait=True)#,

seq.append(name='15th element', wfname=sequence_name + '_element15', trigger_wait=True)#,

seq.append(name='16th element', wfname=sequence_name + '_element16', trigger_wait=True)#,

seq.append(name='17th element', wfname=sequence_name + '_element17', trigger_wait=True)#,

seq.append(name='18th element', wfname=sequence_name + '_element18', trigger_wait=True)#,

seq.append(name='19th element', wfname=sequence_name + '_element19', trigger_wait=True)#,

seq.append(name='20th element', wfname=sequence_name + '_element20', trigger_wait=True)#,

seq.append(name='21st element', wfname=sequence_name + '_element21', trigger_wait=True)#,

AWG.program_awg(seq,test_element1,test_element2,test_element3,test_element1,test_element2,test_element3,test_element4,test_element5,
test_element6,test_element7,test_element8,test_element9,test_element10,test_element11,
test_element12,test_element13,test_element14,test_element15,test_element16,test_element17,
test_element18,test_element19,test_element20,test_element21, verbose = True)#, test_element2)

AWG.AWGrun()
  