"""PNA testing script

Script used to test VNA/PNA behavior with operations that should be common
to all VNAs

"""

import stlab
from stlab.devices.PNAN5221A import PNAN5221A as pnaclass
#from stlab.devices.PNAN5222A import PNAN5222A as pnaclass
#from stlab.devices.RS_ZND import RS_ZND_pna as pnaclass
#from stlab.devices.FieldfoxPNA import FieldfoxPNA as pnaclass

from matplotlib import pyplot as plt

pna = pnaclass(addr='TCPIP::192.168.1.105::INSTR',reset=False,verb=True)

pna.SetRange(4e9,8e9)
pna.SetIFBW(1000.)
pna.SetPower(-25.6)
pna.SetPoints(2001)

data = pna.MeasureScreen()
keys = list(data.keys())
print(keys)
for i in range(0,int((len(keys)-1)/3)):
    x = data[keys[0]]
    y = data[keys[3*(i+1)]]
    plt.plot(x,y)
plt.show()

pna.SetRange(1e9,3e9)
pna.SetPoints(501)
pna.SetIFBW(10e3)
pna.SetPower(-5.)

data = pna.MeasureScreen()
keys = list(data.keys())
print(keys)
for i in range(0,int((len(keys)-1)/3)):
    x = data[keys[0]]
    y = data[keys[3*(i+1)]]
    plt.plot(x,y)
plt.show()

