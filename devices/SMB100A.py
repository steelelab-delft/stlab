# Driver for R&S SMB100A signal generator.  Inherits from instrument class.

import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%12.8e' % mystr


class SMB100A_SG(instrument):
    def __init__(self,addr='TCPIP::192.168.1.43::INSTR',reset=True):
        super(SMB100A_SG, self).__init__(addr,reset)
        self.id()
