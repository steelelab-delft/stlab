import sys

sys.path.append("C:\lib\stlab\devices\Tektronics_Sequencer")

from stlab.devices.Tektronix_AWG520 import Tektronix_AWG520
# from stlab.devices.rigol_DS1054 import Rigol_DS1054
# from stlab.devices.RS_FSV import RS_FSV

import AWG_station

import element
import Pulse_lib as pulse
import sequence

import viewer


def setup_AWG_pulsed_spec_sequence(sequence_name='Cool_Sequence',
                                   measurement_trigger_delay=2e-6,
                                   SSB_modulation_frequency=-50e6,
                                   measurement_pulse_length=10e-6,
                                   measurement_pulse_amp=0.5,
                                   cooling_pulse_length=200e-6,
                                   cooling_measurement_delay=5e-6,
                                   doplot=True,
                                   devAWG=Tektronix_AWG520(name='AWG')):
    '''
    makes the AWG single element sequences for the cooling experiment.
    It contains a cooling pulse, a readout trigger and a readout pulse.
    readout trigger is the fixpoint, as it defines the timing we see on
    the signal analyzer.
    readout pulse is defined with the IQ modulation of a vector source.
    Cooling pulse is a marker to a microwave switch.

    There is some funky stuff happening if there is no buffers around the
    sequence, therefore we have buffer pulses at the beginning and end
    such that the channels are zero there!
    '''

    buffer_pulse_length = 0.1e-6
    readout_trigger_length = 1.0e-6

    AWG = AWG_station.AWG_Station()
    AWG.AWG = devAWG

    clock = devAWG.get_clock()

    devAWG.set_run_mode('ENH')
    devAWG.set_refclock_ext()

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

    sin_pulse = pulse.CosPulse(channel='RF1', name='A sine pulse on RF')
    sin_pulse_2 = pulse.CosPulse(channel='RF2', name='A sine pulse on RF')

    SSB_pulse = pulse.MW_IQmod_pulse(
        I_channel='RF1', Q_channel='RF2', name='SSB pulse')

    pulsed_spec_pulse = pulse.SquarePulse(
        channel='MW_pulsemod', name='A square pulse on MW pmod')

    readout_trigger_pulse = pulse.SquarePulse(
        channel='readout_trigger', name='A square pulse on MW pmod')

    readout_trigger_pulse = pulse.SquarePulse(
        channel='readout_trigger', name='A square pulse on MW pmod')

    sq_pulse_ch1 = pulse.SquarePulse(
        channel='RF1', name='A square pulse on MW pmod')

    sq_pulse_ch2 = pulse.SquarePulse(
        channel='RF2', name='A square pulse on MW pmod')

    test_element1 = element.Element(
        (sequence_name + '_element1'),
        pulsar=AWG, clock=clock)  #, ignore_offset_correction=True)
    test_element2 = element.Element(
        (sequence_name + '_element2'),
        pulsar=AWG, clock=clock)  #, ignore_offset_correction=True)

    test_element1.add(
        pulse.cp(
            readout_trigger_pulse, amplitude=1.,
            length=readout_trigger_length),
        start=0.1e-6,
        name='readout trigger',
        refpoint='start')

    test_element1.add(
        pulse.cp(
            SSB_pulse,
            mod_frequency=SSB_modulation_frequency,
            amplitude=measurement_pulse_amp,
            length=measurement_pulse_length),
        start=measurement_trigger_delay,
        name='readout pulse',
        refpulse='readout trigger',
        refpoint='start')

    test_element1.add(
        pulse.cp(pulsed_spec_pulse, amplitude=1., length=cooling_pulse_length),
        start=-1 * cooling_measurement_delay - cooling_pulse_length,
        name='pulsed spec',
        refpulse='readout pulse',
        refpoint='start')

    test_element1.add(
        pulse.cp(
            readout_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='pulsed spec',
        refpoint='start')

    test_element1.add(
        pulse.cp(
            readout_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout pulse',
        refpoint='end')

    test_element2.add(
        pulse.cp(
            readout_trigger_pulse, amplitude=1.,
            length=readout_trigger_length),
        start=0.1e-6,
        name='readout trigger',
        refpoint='start')

    test_element2.add(
        pulse.cp(
            SSB_pulse,
            mod_frequency=SSB_modulation_frequency,
            amplitude=measurement_pulse_amp,
            length=measurement_pulse_length),
        start=measurement_trigger_delay,
        name='readout pulse',
        refpulse='readout trigger',
        refpoint='start')

    test_element2.add(
        pulse.cp(pulsed_spec_pulse, amplitude=1., length=cooling_pulse_length),
        start=-1 * cooling_measurement_delay - cooling_pulse_length,
        name='pulsed spec',
        refpulse='readout pulse',
        refpoint='start')

    test_element2.add(
        pulse.cp(
            readout_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=-1 * buffer_pulse_length,
        name='buffer left',
        refpulse='pulsed spec',
        refpoint='start')

    test_element2.add(
        pulse.cp(
            readout_trigger_pulse, amplitude=0., length=buffer_pulse_length),
        start=0,
        name='buffer right',
        refpulse='readout pulse',
        refpoint='end')

    #print('Channel definitions: ')

    #test_element1.print_overview()

    # test_element2.print_overview()

    # -------------------------continue-------------------------------

    # -------------------------------------------------------
    # viewing of the sequence for second check of timing etc
    if doplot is True:
        viewer.show_element_stlab(
            test_element1, delay=False, channels='all', ax=None)
        viewer.show_element_stlab(
            test_element2, delay=False, channels='all', ax=None)

    # --------------------------------------------------------

    devAWG.init_dir()
    devAWG.clear_waveforms()
    seq = sequence.Sequence(sequence_name)
    seq.append(
        name='first_element',
        wfname=(sequence_name + '_element1'),
        trigger_wait=True,
        goto_target='second element')

    seq.append(
        name='second_element',
        wfname=(sequence_name + '_element2'),
        trigger_wait=True,
        goto_target='first_element')

    AWG.program_awg(
        seq, test_element1, test_element2, verbose=True)  #, test_element2)
