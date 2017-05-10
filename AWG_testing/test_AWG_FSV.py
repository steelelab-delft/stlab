import numpy as np
import time
import element
import Pulse_lib as pulse
import AWG_station
import RS_FSV_station 
import sequence
import pprint
import imp
import viewer
from AWG520_driver_beta import Tektronix_AWG520
from matplotlib import pyplot as plt

imp.reload(pulse)
imp.reload(element)
imp.reload(AWG_station)
imp.reload(RS_FSV_station)
imp.reload(viewer)

plt.close('all')

#------------------------------------------------------
# Define all the channels on AWG through AWG_station.
# This then again uses the low level AWG driver to communicate with the AWG instrument
# So one never uses the low level AWG driver directly but instead through an interface 
AWG = AWG_station.AWG_Station()
AWG.AWG = Tektronix_AWG520(name='AWG')




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
# train = pulse.clock_train(channel='trigger', name='A sine pulse on RF')


sq_pulse = pulse.SquarePulse(channel='MW_pulsemod',
                             name='A square pulse on MW pmod')


trig_pulse = pulse.SquarePulse(channel = 'trigger', name = "trig pulse for FSV")
test_element1 = element.Element('test_AWG_FSV', pulsar = AWG, ignore_offset_correction=True)

# we copied the channel definition from out global pulsar

# create a few of those
test_element1.add(pulse.cp(sq_pulse, amplitude=1 , length=1e-6),
                 name='first pulse')
test_element1.add(pulse.cp(trig, amplitude=1, length=40e-9), start = 10e-9,
                 name='second pulse', refpulse='first pulse', refpoint='end')



print('Channel definitions: ')

test_element1.print_overview()



#-------------------------continue-------------------------------

# -------------------------------------------------------
# viewing of the sequence for second check of timing etc
viewer.show_element_stlab(test_element1, delay = False, channels = 'all', ax = None)


#--------------------------------------------------------


# #-------------------------------------------------------
# # now to send everything to the AWG, we have perform the last step by putting everything 
# # into a sequence

seq = sequence.Sequence('A Sarwan')
seq.append(name='first_element', wfname='test_AWG_FSV', trigger_wait=True)




AWG.program_awg(seq,test_element1, verbose = True)

AWG.AWGrun()


Read_instr = RS_FSV_station.RS_FSV_station()
Read_instr.prepare()
Read_instr.measure()
Read_instr.get_values()

