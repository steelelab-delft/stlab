"""Module for instance of a Keithley DMM6500

This module contains the functions necessary to control and read data from 
a Keithley DMM6500. It inherits from the Keithley 2100.

"""

from stlab.devices.Keithley_2100 import Keithley_2100


def numtostr(mystr):
    # return '%20.10f' % mystr
    return '%20.15e' % mystr


class Keithley_6500(Keithley_2100):
    def __init__(self,
                 addr='TCPIP::192.168.1.161::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)

    def ResetTrig(self):  # reset trigger model
        self.write('TRIG:LOAD "Empty"')

    def PauseTrig(self):  # pauses measurement
        self.write('TRIG:PAUS')

    def ClearTrace(self):
        self.write(':TRACe:CLEar')

    def ClearBuffer(self):  # clear buffer
        self.write('TRIG:BLOC:BUFF:CLEAR 1')

    def SetSimpleLoop(self, n=10):  # load simple loop
        self.ResetTrig()
        self.ClearBuffer()
        mystr = mystr = 'TRIG:LOAD "SimpleLoop", %s' % (n)
        self.write(mystr)

    def TrigAndWait(self):
        self.write('INIT')
        self.write('*WAI')

    def GetTraceData(self, buffer="defbuffer1", start=1, stop=10):
        # returns the entire trace data stored in buffer
        mystr = 'TRAC:DATA? %s, %s, "%s", READ, REL' % (start, stop, buffer)
        trace = self.query(mystr)
        return float(trace)
