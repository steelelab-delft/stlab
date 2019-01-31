import numpy as np
from stlab.devices.Keithley_2100 import Keithley_2100

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class Keithley_6500(Keithley_2100):
    def __init__(self,addr='TCPIP::192.168.1.161::INSTR',reset=True,verb=True):
        super().__init__(addr,reset,verb)
