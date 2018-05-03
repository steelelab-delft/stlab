# Driver for R&S SMB100A signal generator.  Inherits from instrument class.

import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%12.8e' % mystr


class RS_SGS100A(instrument):
    def __init__(self,addr='TCPIP::192.168.1.43::INSTR',reset=True,verb=True):
        super().__init__(addr,reset,verb)
        self.id()
    def setCWfrequency(self,frec):
        mystr =  numtostr(frec)
        mystr = 'FREQ:CW ' + mystr
        self.write(mystr)
    def getCWfrequency(self):
        mystr = 'FREQ:CW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    def setCWphase(self,phase):
        mystr = 'SOUR:PHAS %.2f' %phase
        self.write(mystr)
    def getCWphase(self):
        mystr = 'SOUR:PHAS?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    def setCWpower(self,x):
        mystr =  numtostr(x)
        mystr = 'SOUR:POW:POW ' + mystr
        self.write(mystr)
    def getCWpower(self):
        mystr = 'SOUR:POW:POW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    def RFon(self):
        self.write('OUTP ON')
    def RFoff(self):
        self.write('OUTP OFF')
    def IQon(self):
        self.write('IQ:STATe ON')
    def IQoff(self):
        self.write('IQ:STATe OFF')