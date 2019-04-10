import stlab
from stlab.devices.PNAN5222A import PNAN5222A
import numpy as np
import stlab.advanced_measurements.TwoToneSpectroscopy as tts


prefix = 'B' #prefix for measurement folder name.  Can be anything or empty
idstring = 'TwoToneTest' #Additional info included in measurement folder name.  Can be anything or empty


pna = PNAN5222A(addr='TCPIP::192.168.1.221::INSTR',reset=True,verb=True) #Initialize device communication and reset
tts.TwoToneSetup(pna,
        f_probe_start = 5.8e9,
        f_probe_stop = 6.0e9,
        f_probe_points = 1001,
        probe_ifbw = 10,
        probe_power = 0,
        f_pump_start = 5.1e9,
        f_pump_stop = 5.3e9,
        f_pump_points = 201,
        pump_ifbw = 10,
        pump_power = 0,
        searchtype='MAX')

f_probe = tts.TwoToneProbeSet(pna,searchtype='MAX')

tts.TwoToneSetProbeFrequency(pna,f_probe)
result = tts.TwoToneMeasure(pna)

myfile = stlab.newfile(prefix,idstring + '_1',autoindex=True)
stlab.saveframe(myfile,result[1])
stlab.metagen.fromarrays(myfile,result[1]['Frequency (Hz)'],[0],xtitle='Frequency (Hz)',ytitle='Nothing',colnames='auto')

myfile = stlab.newfile(prefix,idstring + '_2',autoindex=True)
stlab.saveframe(myfile,result[0])
stlab.metagen.fromarrays(myfile,result[0]['Frequency (Hz)'],[0],xtitle='Frequency (Hz)',ytitle='Nothing',colnames='auto')


myfile.close()
tts.TwoToneSourcesOff(pna)
