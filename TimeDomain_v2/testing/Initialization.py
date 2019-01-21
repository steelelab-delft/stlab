"""
This scripts initializes the instruments and imports the modules
"""


# General imports

import time
import logging
t0 = time.time()  # to print how long init takes

from importlib import reload  # Useful for reloading while testing
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Qcodes
import qcodes as qc
# currently on a Windows machine
# qc.set_mp_method('spawn')  # force Windows behavior on mac
# qc.show_subprocess_widget()
# Globally defined config
# qc_config = {'datadir': r'D:\\Experimentsp7_Qcodes_5qubit',
#              'PycQEDdir': 'D:\GitHubRepos\PycQED_py3'}
qc_config = {'datadir': r'D:\\measurement_data\\Time_Domain_Beginnings',
             'PycQEDdir': 'C:\\libs\\PycQED_py3'}

# makes sure logging messages show up in the notebook
root = logging.getLogger()
root.addHandler(logging.StreamHandler())

# General PycQED modules
from pycqed.measurement import measurement_control as mc
from pycqed.measurement import sweep_functions as swf
from pycqed.measurement import awg_sweep_functions as awg_swf
from pycqed.measurement import detector_functions as det
from pycqed.measurement import composite_detector_functions as cdet
from pycqed.measurement.optimization import nelder_mead
from pycqed.analysis import measurement_analysis as ma
from pycqed.analysis import analysis_toolbox as a_tools
from pycqed.measurement import awg_sweep_functions_multi_qubit as awg_swf_m
from pycqed.measurement.pulse_sequences import multi_qubit_tek_seq_elts as sq_m

from pycqed.instrument_drivers.physical_instruments import Fridge_monitor as fm
from pycqed.utilities import general as gen
# Standarad awg sequences
from pycqed.measurement.waveform_control import pulsar as ps
from pycqed.measurement.pulse_sequences import standard_sequences as st_seqs
from pycqed.measurement.pulse_sequences import calibration_elements as cal_elts
from pycqed.measurement.pulse_sequences import single_qubit_tek_seq_elts as sq

# Instrument drivers
from qcodes.instrument_drivers.rohde_schwarz import SGS100A as rs

from qcodes.instrument_drivers.Keysight import N51x1 as ks

# import qcodes.instrument_drivers.QuTech.IVVI as iv
# from qcodes.instrument_drivers.agilent.E8527D import Agilent_E8527D

from qcodes.instrument_drivers.tektronix import AWG520 as tk520



import pycqed.instrument_drivers.meta_instrument.qubit_objects.Tektronix_driven_transmon as qbt
from pycqed.instrument_drivers.meta_instrument import heterodyne as hd
import pycqed.instrument_drivers.meta_instrument.CBox_LookuptableManager as lm


#import for UHFKLI for UHFLI
# from pycqed.instrument_drivers.physical_instruments.ZurichInstruments import UHFQuantumController as ZI_UHFQC
# import for ATS
import qcodes.instrument.parameter as parameter
import qcodes.instrument_drivers.AlazarTech.ATS9870 as ATSdriver
import qcodes.instrument_drivers.AlazarTech.ATS_acquisition_controllers as ats_contr




############################
# Initializing instruments #
############################
station = qc.Station()

# Fridge_mon = fm.Fridge_Monitor('Fridge monitor', 'LaMaserati')
# station.add_component(Fridge_mon)

###########
# Sources #
###########
RFLO = ks.N51x1(name='RFLO', address='TCPIP0::192.168.1.91::inst0::INSTR', server_name=None)  #
station.add_component(RFLO)

SPEC = rs.RohdeSchwarz_SGS100A(name='SPEC', address='TCPIP0::192.168.1.37::inst0::INSTR', server_name=None)  #
station.add_component(SPEC)

#Initializing UHFQC
# UHFQC_1 = ZI_UHFQC.UHFQC('UHFQC_1', device='dev2209', server_name=None)
# station.add_component(UHFQC_1)

#initializing AWG
AWG = tk520.Tektronix_AWG520(name='AWG', timeout=1, terminator='\n',
                            address='TCPIP0::192.168.1.27::1234::SOCKET', server_name=None)
station.add_component(AWG)

#Initializaing ATS,
ATSdriver.AlazarTech_ATS.find_boards()
ATS = ATSdriver.AlazarTech_ATS9870(name='ATS', server_name=None)
station.add_component(ATS)

# Configure all settings in the ATS
ATS.config(clock_source='INTERNAL_CLOCK',
                sample_rate=1e9,
                clock_edge='CLOCK_EDGE_RISING',
                decimation=0,
                coupling=['AC','AC'],
                channel_range=[0.04,0.04],
                impedance=[50,50],
                bwlimit=['DISABLED','DISABLED'],
                trigger_operation='TRIG_ENGINE_OP_J',
                trigger_engine1='TRIG_ENGINE_J',
                trigger_source1='EXTERNAL',
                trigger_slope1='TRIG_SLOPE_POSITIVE',
                trigger_level1=128,
                trigger_engine2='TRIG_ENGINE_K',
                trigger_source2='DISABLE',
                trigger_slope2='TRIG_SLOPE_POSITIVE',
                trigger_level2=128,
                external_trigger_coupling='AC',
                external_trigger_range='ETR_5V',
                trigger_delay=0,
                timeout_ticks=0
)

#demodulation frequcnye is first set to 10 MHz
ATS_controller = ats_contr.Demodulation_AcquisitionController(name='ATS_controller',
                                                                      demodulation_frequency=0,
                                                                      alazar_name='ATS',
                                                                      server_name=None)
station.add_component(ATS_controller)

# configure the ATS controller
ATS_controller.update_acquisitionkwargs(#mode='NPT',
                 samples_per_record=64*1000,#4992,
                 records_per_buffer=8,#70, segmments
                 buffers_per_acquisition=100,
                 channel_selection='AB',
                 transfer_offset=0,
                 external_startcapture='ENABLED',
                 enable_record_headers='DISABLED',
                 alloc_buffers='DISABLED',
                 fifo_only_streaming='DISABLED',
                 interleave_samples='DISABLED',
                 get_processed_data='DISABLED',
                 allocated_buffers=100,
                 buffer_timeout=1000
)

HS = hd.HeterodyneInstrument('HS', LO=RFLO, RF=RFLO, AWG=None,
                             acquisition_instr=ATS.name,
                             acquisition_instr_controller=ATS_controller.name,
                             server_name=None)
station.add_component(HS)

# VNA
# VNA = ZNB20.ZNB20(name='VNA', address='TCPIP0::192.168.0.55', server_name=None)  #
# station.add_component(VNA)


MC = mc.MeasurementControl('MC')

MC.station = station
station.MC = MC
station.add_component(MC)

# The AWG sequencer
station.pulsar = ps.Pulsar()
station.pulsar.AWG = station.components['AWG']
for i in range(2):
    # Note that these are default parameters and should be kept so.
    # the channel offset is set in the AWG itself. For now the amplitude is
    # hardcoded. You can set it by hand but this will make the value in the
    # sequencer different.
    station.pulsar.define_channel(id='ch{}'.format(i+1),
                                  name='ch{}'.format(i+1), type='analog',
                                  # max safe IQ voltage
                                  high=1., low=-1.,
                                  offset=0.0, delay=0, active=True)
    station.pulsar.define_channel(id='ch{}_marker1'.format(i+1),
                                  name='ch{}_marker1'.format(i+1),
                                  type='marker',
                                  high=2.0, low=0, offset=0.,
                                  delay=0, active=True)
    station.pulsar.define_channel(id='ch{}_marker2'.format(i+1),
                                  name='ch{}_marker2'.format(i+1),
                                  type='marker',
                                  high=2.0, low=0, offset=0.,
                                  delay=0, active=True)
# to make the pulsar available to the standard awg seqs
st_seqs.station = station
sq.station = station
cal_elts.station = station


def print_instr_params(instr):
    snapshot = instr.snapshot()
    print('{0:23} {1} \t ({2})'.format('\t parameter ', 'value', 'units'))
    print('-'*80)
    for par in sorted(snapshot['parameters']):
        print('{0:25}: \t{1}\t ({2})'.format(
            snapshot['parameters'][par]['name'],
            snapshot['parameters'][par]['value'],
            snapshot['parameters'][par]['units']))