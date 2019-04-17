import stlab
from stlab.devices.PNAN5222A import PNAN5222A
import numpy as np



prefix = '' #prefix for measurement folder name.  Can be anything or empty
idstring = 'two_tone' #Additional info included in measurement folder name.  Can be anything or empty



pna = PNAN5222A(addr='TCPIP::192.168.1.42::INSTR',reset=False,verb=True) #Initialize device communication and reset
pna.TwoToneSetup(
        f_probe_start = 5.54e9,
        f_probe_stop = 5.545e9,
        f_probe_points = 51,
        probe_ifbw=100,
        probe_power = 25,
        f_pump_start = 7.5e9,
        f_pump_stop = 12.5e9,
        f_pump_points = 20001,
        pump_ifbw = 200,
        pump_power = -5)

f_probe = pna.TwoToneProbeForMin()
pna.TwoToneSetProbeFrequency(f_probe)
result = pna.TwoToneMeasure()

myfile = stlab.newfile(prefix,idstring,result[1].keys())
stlab.savedict(myfile,result[1])
stlab.metagen.fromarrays(myfile,result[1]['Frequency (Hz)'],[0],xtitle='Pump frequency (Hz)',ytitle='Nothing',colnames=result[1].keys())

myfile.close()
pna.TwoToneSourcesOff()
