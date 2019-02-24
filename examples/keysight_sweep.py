"""Keysight SMU sweeping functionality test

Script used to measure using Keysight SMU without setting/getting with every
current/voltage step.  Instead this uses the internal sweeping functions of
the SMU.

"""

import stlab
from stlab.devices.keysight import keysightB2901A as sourceclass
from matplotlib import pyplot as plt

dev = sourceclass(addr='TCPIP::192.168.1.63::INSTR', reset=True)
'''
dev.write("*RST")
dev.write(":sour:func:mode volt")
dev.write(":sour:volt:mode swe")
dev.write(":sour:volt:star 0")
dev.write(":sour:volt:stop 0.1")
dev.write(":sour:volt:poin 5")
dev.write(':sens:func "curr"')
dev.write(":sens:curr:nplc 0.1")
dev.write(":sens:curr:prot 0.1")
dev.write(":trig:sour aint")
dev.write(":trig:coun 5")
dev.write(":outp on")
dev.write(":init (@1)")
result = dev.query(":fetc:arr:curr? (@1)")
print(result)
'''

dev.SetModeCurrent()
dev.SetSweep()
dev.SetStartStop(0, 3e-6)
dev.SetPoints(101)
dev.write('SWE:RANG BEST')
dev.write('SWE:DIR UP')
dev.write('SWE:SPAC LIN')
dev.write('SWE:STA DOUB')
dev.write('SENS:FUNC "VOLT"')
dev.write('SENS:VOLT:RANG 1.')
dev.write('SENS:VOLT:NPLC 1')
dev.write('SENS:VOLT:PROT 1')
dev.write('TRIG:SOUR AINT')
dev.write('TRIG:COUN 202')
dev.write('OUTP ON')
dev.query('INIT; *OPC?')
x = dev.query('FETC:ARR:CURR?')
y = dev.query('FETC:ARR:VOLT?')
dev.write('OUTP OFF')
x = x.strip().split(',')
y = y.strip().split(',')
x = [float(xx) for xx in x]
y = [float(xx) for xx in y]
plt.plot(x, y)
plt.show()
