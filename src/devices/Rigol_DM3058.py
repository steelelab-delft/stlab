"""Module for instance of a Rigol DM3058 digital multimeter

This module contains the functions necessary to control and read data from 
a Rigol DM3058 digital multimeter. It inherits from instrument class.

"""

import numpy as np
from stlab.devices.instrument import instrument


def numtostr(mystr):
    return '%12.8e' % mystr


class Rigol_DM3058(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.216::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(
            addr, reset, verb, write_termination='\n', read_termination='\n')
        self.id()

    def write(self, mystr):
        mystr = ':' + mystr
        if self.verb:
            print(mystr)
        self.dev.write(mystr)

    def query(self, mystr):
        mystr = ':' + mystr
        if self.verb:
            print(mystr)
        out = self.dev.query(mystr)
        return out

    def GetVoltage(self):
        mystr = 'MEAS:VOLT:DC?'
        volt = self.query(mystr)
        volt = volt.split(" ")
        volt = float(volt[-1])
        return volt

    def SetRange(self, i):  #0: 200 mV, 1: 2 V, 2: 20 V, 3: 200 V, 4: 1000 V
        self.SetRangeAuto(False)
        mystr = "MEAS:VOLT:DC %d" % i
        self.write(mystr)

    def SetRangeAuto(self, state=True):
        if state:
            self.write('MEAS AUTO')
        else:
            self.write('MEAS MANU')

    def SetSpeed(self, value='S'):  #S,M or F (slow, medium, fast)
        self.write('RATE:VOLTage:DC %s' % value)
        return

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass


'''
        def GetVoltCurr(self):
        mystr = 'FORM:ELEM:SENS VOLT,CURR'
        self.write(mystr)
        mystr = ':MEAS?'
        outstr = self.query(mystr)
        data = np.array(list(map(float, outstr.split(','))))
        return (data[0],data[1])
'''
