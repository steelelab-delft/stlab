import visa
import numpy as np
import time
from stlab.devices.instrument import instrument

class PhaseMatrix_FSW0020(instrument):
    def __init__(self,addr='TCPIP::192.168.1.220::10001::SOCKET',reset=True,verb=True):
        super().__init__(addr,reset,verb=verb,read_termination='\n',write_termination='\n')
        self.id()

    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass
