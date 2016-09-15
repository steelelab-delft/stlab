import visa
import numpy as np
from stlab.devices.instrument import instrument
from stlab.devices.PNAN5221A import PNAN5221A

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class PNAN5222A(PNAN5221A):
    def __init__(self,addr='TCPIP::192.168.1.42::INSTR',reset=True,verb=True):
        super(PNAN5222A, self).__init__(addr,reset,verb)
