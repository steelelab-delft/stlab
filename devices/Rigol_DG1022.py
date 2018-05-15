# Driver for R&S SMB100A signal generator.  Inherits from instrument class.

import visa
import numpy as np
from stlab.devices.instrument import instrument
import time

def numtostr(mystr):
    return '%12.8e' % mystr


class Rigol_DG1022(instrument):
    def __init__(self,addr='USB0::0x1AB1::0x0588::DG1D124204588::INSTR',reset=True,verb=True):
        super().__init__(addr,reset,verb,query_delay=100e-3)
        #self.id()
#    def query(self,mystr):
#        self.write(mystr)
        #time.sleep(10e-3) #Needed so it wont crash...
#        out = self.dev.read()
#        return out
    def SetShape(self,shape,ch = 1): # {SINusoid|SQUare|RAMP|PULSe|NOISe|DC|USER}
        if ch == 1:
            self.write('FUNC {}'.format(shape))
        else:
            self.write('FUNC:CH{} {}'.format(ch,shape))
        time.sleep(1)
        return
    def SetVpp(self,vv,ch=1):
        if ch == 1:
            self.write('VOLT:UNIT VPP') #{VPP|VRMS|DBM}
            self.write('VOLT {}'.format(vv))
        else:
            self.write('VOLT:CH{}:UNIT VPP'.format(ch)) #{VPP|VRMS|DBM}
            self.write('VOLT:CH{} {}'.format(ch,vv))
    def SetVoffset(self, vv, ch=1):
        if ch ==1:
            self.write('VOLT:OFFSET {}'.format(vv))
        else:
            self.write('VOLT:CH{}:OFFSET {}'.format(ch,vv))
        return
    def SetFrequency(self, ff,ch=1):
        if ch == 1:
            self.write('FREQ {}'.format(ff))
        else:
            self.write('FREQ:CH{} {}'.format(ch,ff))
    def SetOn(self,ch=1):
        if ch ==1: 
            self.write('OUTP ON')
        else:
            self.write('OUTP:CH{} ON'.format(ch))
    def SetOff(self,ch=1):
        if ch ==1: 
            self.write('OUTP OFF')
        else:
            self.write('OUTP:CH{} OFF'.format(ch))
    
    