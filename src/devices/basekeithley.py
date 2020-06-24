"""Module implementing basic Keithley digital multimeter

This module is the base class for Keithley DMMs 2000, 2100 and 6500
"""

from stlab.devices.instrument import instrument
from stlabutils.utils.stlabdict import stlabdict as stlabdict


import numpy as np
import pandas as pd
import time

import abc


def numtostr(mystr):
    return '%20.15e' % mystr


class basekeithley(instrument, abc.ABC):
    def __init__(self, addr, reset, verb, **kwargs):
        super().__init__(addr, reset, verb, **kwargs)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None
        self.id()
        if reset:
            self.SetContinuous(False)  #Turn off continuous mode

##### METHODS THAT CAN GENERALLY BE USED ON ALL KEITHLEYs.  REIMPLEMENT IF NECESSARY #######

    def GetVoltage(
            self, range='DEF', res='DEF'
    ):  # (manual entry) Preset and make a DC voltage measurement with the specified range and resolution. The reading is sent to the output buffer.
        # range and res can be numbers or MAX, MIN, DEF
        # Lower resolution means more digits of precision (and slower measurement).  The number given is the voltage precision desired.  If value is too low, the query will timeout
        mystr = 'MEAS:VOLT:DC? %s,%s' % (range, res)
        volt = self.query(mystr)
        return float(volt)

    def GetCurrent(
            self, range='DEF', res='DEF'
    ):  # (manual entry) Preset and make a DC current measurement with the specified range and resolution. The reading is sent to the output buffer.
        # range and res can be numbers or MAX, MIN, DEF
        # Lower resolution means more digits of precision (and slower measurement).  The number given is the voltage precision desired.  If value is too low, the query will timeout
        mystr = 'MEAS:CURR:DC? %s,%s' % (range, res)
        num = self.query(mystr)
        return float(num)

# If using GetVoltage(), the following settings are ignored

    def SetRangeAuto(self, set=True):
        mystr = "SENS:" + self.GetFunction() + ":RANGE:AUTO %d" % int(set)
        self.write(mystr)

    def SetRange(self, range):
        self.SetRangeAuto(False)
        func = self.GetFunction()
        if isinstance(range, str):
            mystr = 'SENS:' + func + ':RANGE %s' % range
        else:
            mystr = 'SENS:' + func + ':RANGE %f' % range
        self.write(mystr)

    def SetDisplay(self, state=True):
        if state:
            self.write('DISP ON')
        else:
            self.write('DISP OFF')

    def SetFunction(self, mystr):
        self.write('FUNC ' + mystr)

    def GetFunction(self):
        mystr = self.query('FUNC?')
        mystr = mystr.strip("'").strip('"').strip("'")
        if mystr == 'VOLT':
            mystr = 'VOLT:DC'
        return mystr

    def Trigger(self):
        self.write('INIT')

    def SetContinuous(self, state=True):
        if state:
            self.write('TRIG:COUN INF')
        else:
            self.write('TRIG:COUN 1')

    def ReadValue(self):
        #self.SetContinuous(False)
        return self.query('READ?')

    def GetVoltageFast(self):
        x = self.GetMeasurement()
        return x

    def GetMeasurement(self):
        self.Trigger()
        x = float(self.ReadValue())
        return x

    def SetNPLC(self, n=1):
        self.write('VOLT:NPLC ' + str(n))

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass

##### ABSTRACT METHODS TO BE IMPLEMENTED ON A PER KEITHLEY BASIS #####################

    @abc.abstractmethod
    def FastMeasurementSetup(self):
        self.SetRangeAuto(False)
        self.SetRange(10)
        self.SetNPLC(1)
        self.write('TRIG:SOUR IMM')
        self.write('SENS:GAIN:AUTO OFF')
        self.write('SENS:ZERO:AUTO OFF')


##### FULLY IMPLEMENTED METHODS THAT DO NOT NEED TO BE REIMPLEMENTED (BUT CAN BE IF NECESSARY) #####################