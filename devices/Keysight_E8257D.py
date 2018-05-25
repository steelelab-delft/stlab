# Driver for R&S SMB100A signal generator.  Inherits from instrument class.

import visa
import numpy as np
from stlab.devices.instrument import instrument


def numtostr(mystr):
    return '%12.8e' % mystr


class Keysight_E8257D(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.66::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.id()

    def setCWfrequency(self, frec):
        mystr = numtostr(frec)
        mystr = 'FREQ:CW ' + mystr
        self.write(mystr)

    def getCWfrequency(self):
        mystr = 'FREQ:CW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def setCWpower(self, x):
        mystr = numtostr(x)
        mystr = 'SOUR:POW ' + mystr
        self.write(mystr)

    def getCWpower(self):
        mystr = 'SOUR:POW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def RFon(self):
        self.write('OUTP ON')

    def RFoff(self):
        self.write('OUTP OFF')

    def set_reference(self, val):
        '''
        sets the 10 MHz reference source to INTernal or EXTernal.
        '''
        self.write(':SOURce:ROSCillator:SOURce ' + val)

    def get_reference(self, val):
        '''
        gets the 10 MHz reference source
        '''
        bla = self.query(':SOURce:ROSCillator:SOURce?')
        print(bla)

    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass
