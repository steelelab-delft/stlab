"""Module for instance of a R&S SMB100A signal generator

This module contains the functions necessary to control and read data from 
a R&S SMB100A signal generator. It inherits from instrument class.

"""

from stlab.devices.instrument import instrument


def numtostr(mystr):
    return '%12.8e' % mystr


class RS_SMB100A(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.43::INSTR',
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

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass
