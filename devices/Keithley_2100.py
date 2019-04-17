"""Module for instance of a Keithley 2100

This module contains the functions necessary to control and read data from 
a Keithley 2100 multimeter. It inherits from basekeithley.

"""
from stlab.devices.basekeithley import basekeithley


class Keithley_2100(basekeithley):
    def __init__(self,
                 addr='USB0::0x05E6::0x2100::1310646::INSTR',
                 reset=True,
                 verb=True,
                 **kwargs):
        super().__init__(addr, reset, verb, **kwargs)

    def FastMeasurementSetup(self):
        self.SetRangeAuto(False)
        self.SetRange(10)
        self.SetNPLC(1)
        self.write('TRIG:SOUR IMM')
        self.write('SENS:GAIN:AUTO OFF')
        self.write('SENS:ZERO:AUTO OFF')