import stlab
from stlab.devices.PNAN5222A import PNAN5222A
import numpy as np
import stlab.advanced_measurements.TwoToneSpectroscopy as tts


prefix = '' #prefix for measurement folder name.  Can be anything or empty
idstring = 'two_tone_pump_sweep' #Additional info included in measurement folder name.  Can be anything or empty


pna = PNAN5222A(addr='TCPIP::192.168.1.221::INSTR',reset=True,verb=True) #Initialize device communication and reset

f_res = 6.487e9
f_probe_range = 3e6

delta_f_pump_start = -25e6
delta_f_pump_end = 5e6

tts.TwoToneSetup(pna,
        f_probe_start = f_res-f_probe_range,
        f_probe_stop = f_res+f_probe_range,
        f_probe_points = 10001,
        probe_ifbw = 10e3,
        probe_power = 0,
        f_pump_start = f_res+delta_f_pump_start,
        f_pump_stop = f_res+delta_f_pump_end,
        f_pump_points = 100e3,
        pump_ifbw = 10e3,
        pump_power = 30,
        searchtype='MIN')

f_probe = tts.TwoToneProbeSet(pna,searchtype='MIN')

tts.TwoToneSetProbeFrequency(pna,f_probe)
result = tts.TwoToneMeasure(pna)

myfile = stlab.newfile(prefix,idstring + '')
stlab.saveframe(myfile,result[1])
stlab.metagen.fromarrays(myfile,result[1]['Frequency (Hz)'],[0],xtitle='Frequency (Hz)',ytitle='Nothing',colnames='auto')

myfile = stlab.newfile(prefix,idstring + '_finding_res')
stlab.saveframe(myfile,result[0])
stlab.metagen.fromarrays(myfile,result[0]['Frequency (Hz)'],[0],xtitle='Frequency (Hz)',ytitle='Nothing',colnames='auto')


myfile.close()
tts.TwoToneSourcesOff(pna)
