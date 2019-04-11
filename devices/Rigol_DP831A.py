"""Module for instance of a Rigol DP831A power supply

This module contains the functions necessary to control and read data from 
a Rigol DP831A power supply. It inherits from instrument class.

"""

import numpy as np
from stlab.devices.instrument import instrument
import time


class Rigol_DP831A(instrument):
    def __init__(self,
                 addr='USB0::0x1AB1::0x0588::DG1D124204588::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        #super().__init__(addr,reset,verb,query_delay=100e-3)

    def SetOutputOn(self, ii=1):
        self.write('OUTP CH{},ON'.format(ii))
        return

    def SetOutputOff(self, ii=1):
        self.write('OUTP CH{},OFF'.format(ii))
        return

    def SetVoltage(self, vv, ii=1):
        self.write('SOUR{}:VOLT {}'.format(ii, vv))
        return

    def GetVoltage(self, ii=1):
        result = float(self.query('SOUR{}:VOLT?'.format(ii)))
        return result

    def SetCurrent(self, cc, ii=1):
        self.write('SOUR{}:CURR {}'.format(ii, cc))
        return

    def GetCurrent(self, ii=1):
        result = float(self.query('SOUR{}:CURR?'.format(ii)))
        return result

    def RampVoltage(self, v1, ii=1, tt=5, steps=100):
        v0 = self.GetVoltage(ii)
        if np.abs(v0 - v1) < 0.001:
            self.SetVoltage(ii, v1)
            return
        voltages = np.linspace(v0, v1, steps)
        twait = tt / steps
        for vv in voltages:
            self.SetVoltage(vv, ii)
            time.sleep(twait)