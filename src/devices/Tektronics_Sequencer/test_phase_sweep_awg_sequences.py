
import sys

sys.path.append("C:\\libs\\stlab\\AWG_testing\\")

from stlab.devices.RS_SGS100A import RS_SGS100A
from AWG520_driver_beta import Tektronix_AWG520
from stlab.devices.rigol_DS1054 import Rigol_DS1054
from stlab.devices.RS_FSV import RS_FSV

import AWG_station

import element
import Pulse_lib as pulse
import sequence

import viewer
import imp
import numpy as np


AWG = AWG_station.AWG_Station()
devAWG = Tektronix_AWG520(name='AWG')


AWG.AWG = devAWG

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

SSB_pulse = pulse.MW_IQmod_pulse(I_channel ='RF2', Q_channel='RF1', name='SSB pulse')

sq_pulse = pulse.SquarePulse(channel='trigger',
                             name='A square pulse on MW pmod')

phases = np.linspace(0, 360, 37)

for i, phase in enumerate(phases):

    devAWG.init_dir()

    seq = sequence.Sequence('phase_%d' %phase)

    phases = np.linspace(0, 360, 37)

    print(phases)

    elements = []


    elem = element.Element('phase_%d' %phase, pulsar = AWG)#, ignore_offset_correction=True)


    # create a few of those
    elem.add(pulse.cp(sq_pulse, amplitude=1., length=0.5e-6), start = 0.2e-6,
                     name='first pulse', refpoint='start')

    elem.add(pulse.cp(SSB_pulse, mod_frequency=-50e6, amplitude=0.5, length=20.0e-6, phase=phase), start = 5.0e-6,
                     name='second pulse', refpulse = 'first pulse', refpoint='end')

    elements.append(elem)

    if phase == 360:
        seq.append(name='phase_%d' %phase, wfname='phase_%d' %phase, trigger_wait=True,
               goto_target='phase_%d' %0.)
    else:
        seq.append(name='phase_%d' %phase, wfname='phase_%d' %phase, trigger_wait=True,
               goto_target='phase_%d' %phases[i+1])

    print('Channel definitions: ')

    elem.print_overview()


    AWG.program_awg(seq, *elements, verbose = True)#, test_element2)
