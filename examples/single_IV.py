"""IVVI single IV

Example script for measuring a single IV curve using the TU Delft IVVI rack and a Keithley DMM6500 as voltmeter

"""

import stlab
from stlab.devices.IVVI import IVVI_DAC
import numpy as np
import time
from stlab.devices.TritonWrapper import TritonWrapper

# Temperature readout
mytriton = TritonWrapper()
T = mytriton.gettemperature(8)

# IVVI
ivvi = IVVI_DAC(addr='COM5', verb=True)
ivvi.RampAllZero(tt=10.)
isgain = 10e-6  # A/V gain for isource (forward bias)
isdac = 3  # dac number for isource
islist = np.arange(-10.1e-6, 10.1e-6, 0.1e-6)

# Keithley
vmeas = stlab.adi(addr='TCPIP::192.168.1.161::INSTR',
                  verb=True, read_termination='\n')
vmeas.SetRangeAuto(False)
vmeas.SetRange(10)
vmeas.write('VOLT:NPLC 1')
vmgain = 1000  # V/V gain for vmeas

prefix = 'F'
idstring = 'single_IV'

colnames = ['Time (s)', 'T (K)', 'Iset (A)', 'Vmeas (V)']

last_time = time.time()

myfile = stlab.newfile(prefix, idstring, colnames, autoindex=True)
# Take curr in amps, apply gain and convert to millivolts
ivvi.RampVoltage(isdac, islist[0]/isgain*1e3, tt=10.)

for curr in islist:
    print('\n####### Iset (A):', curr)
    # Take curr in amps, apply gain and convert to millivolts
    ivvi.SetVoltage(isdac, curr/isgain*1e3)
    # Measure output voltage of IVVI and apply output gain
    vm = float(vmeas.query('READ?'))/vmgain
    isset = curr
    current_time = time.time()
    line = [current_time - last_time, T, isset, vm]
    stlab.writeline(myfile, line)

myfile.write('\n')
stlab.metagen.fromarrays(
    myfile, islist, [0], xtitle='Is (A)', ytitle='None ()', colnames=colnames)

ivvi.RampAllZero(tt=10.)
ivvi.close()
vmeas.close()
