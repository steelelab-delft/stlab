"""Module for instance of a Keysight N9010B EXA signal analyzer

This module contains the functions necessary to control and read data from 
a Keysight N9010B EXA signal analyzer. It inherits from instrument class.

"""
from stlab.devices.instrument import instrument
from stlab.utils.stlabdict import stlabdict
import numpy as np
import pandas as pd


class Keysight_N9010B(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.216::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.dev.timeout = None

    def SetDigitalIFBW(self, x):
        mystr = 'WAV:DIF:BAND {}'.format(x)
        self.write(mystr)

    def GetDigitalIFBW(self):
        mystr = 'WAV:DIF:BAND?'
        x = self.query(mystr)
        return float(x)

    def SetSampleRate(self, x):
        mystr = 'WAV:SRAT {}'.format(x)
        self.write(mystr)

    def GetSampleRate(self):
        mystr = 'WAV:SRAT?'
        x = self.query(mystr)
        return float(x)

    def SetIQSweepTime(self, x):
        mystr = 'WAVeform:SWEep:TIME {}'.format(x)
        self.write(mystr)

    def GetIQSweepTime(self):
        mystr = 'WAVeform:SWEep:TIME?'
        x = self.query(mystr)
        return float(x)

    def SetContinuous(self, state=True):
        if state:
            self.write('INIT:CONT 1')
        else:
            self.write('INIT:CONT 0')
        return

    def GetSweepTime(self):
        sweeptime = self.query('SWE:TIME?')
        return float(sweeptime)

    def MeasureIQ(self):
        self.SetContinuous(False)
        result = self.query(':READ:WAVeform0?')
        result = result.split(',')
        result = [float(x) for x in result]
        result = np.asarray(result)
        I = result[::2]
        Q = result[1::2]
        print('result lenght', type(result), len(result))
        print('I lenght', type(result), len(I))
        print('Q lenght', type(result), len(Q))
        tend = self.GetIQSweepTime()
        t = np.linspace(0, tend, len(I) + 1)
        t = t[1:]
        #print((t[1]-t[0]))
        #print(1/(t[1]-t[0]))
        #print(self.GetSampleRate())
        output = pd.DataFrame()
        output['Time (s)'] = t
        output['I (V)'] = I
        output['Q (V)'] = Q
        output['Digital IFBW (Hz)'] = self.GetDigitalIFBW()
        return output

    def MeasureScreen(self):
        self.SetContinuous(False)
        result = self.query('READ:SAN?')
        result = result.split(',')
        result = [float(x) for x in result]
        result = np.asarray(result)
        xx = result[::2]
        yy = result[1::2]
        #output = stlabdict()
        output = pd.DataFrame()
        output['Frequency (Hz)'] = xx
        output['PSD (dBm)'] = yy
        output['Res BW (Hz)'] = self.GetResolutionBW()
        return output