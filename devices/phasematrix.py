import visa
import numpy as np
import time
from stlab.devices.instrument import instrument

class PhaseMatrixFSW0020(instrument):
    def __init__(self,addr='TCPIP::192.168.1.220::10001::SOCKET',reset=True,verb=True):
        super(PhaseMatrixFSW0020, self).__init__(addr,reset,verb=verb,read_termination='\n',write_termination='\n')
        self.id()