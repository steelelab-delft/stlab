# Driver for R&S SMB100A signal generator.  Inherits from instrument class.

import visa
import numpy as np
from instrument import instrument

def numtostr(mystr):
    return '%12.8e' % mystr


class SMB100A_SG(instrument):
    def __init__(self,addr='TCPIP::192.168.1.151::INSTR',reset=True):
        super(SMB100A_SG, self).__init__(addr,reset)
