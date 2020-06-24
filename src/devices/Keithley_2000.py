"""Module for instance of a Keithley 2000

This module contains the functions necessary to control and read data from 
a Keithley 2000 multimeter. It inherits from basekeithley.

"""
from .basekeithley import basekeithley


class Keithley_2000(basekeithley):
    def __init__(self,
                 addr='TCPIP::192.168.1.13::1470::SOCKET',
                 reset=True,
                 verb=True,
                 **kwargs):
        super().__init__(addr, reset, verb, **kwargs)

    def FastMeasurementSetup(self):
        self.SetRangeAuto(False)
        self.SetRange(10)
        self.SetNPLC(1)
        self.write('TRIG:SOUR IMM')
        self.write('SENS:ZERO:AUTO OFF')