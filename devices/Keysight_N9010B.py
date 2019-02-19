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
                 addr='TCPIP::192.168.1.228::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.dev.timeout = None

    def SetStart(self, x):
        mystr = 'FREQ:STAR {}'.format(x)
        self.write(mystr)

    def SetStop(self, x):
        mystr = 'FREQ:STOP {}'.format(x)
        self.write(mystr)

    def SetCenter(self, x):
        mystr = 'FREQ:CENT {}'.format(x)
        self.write(mystr)

    def SetSpan(self, x):
        mystr = 'FREQ:SPAN {}'.format(x)
        self.write(mystr)

    def SetResolutionBW(self, x):
        mystr = 'BAND:RES {}'.format(x)
        self.write(mystr)

    def GetResolutionBW(self):
        mystr = 'BAND:RES?'
        x = self.query(mystr)
        return float(x)

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

    def SetPoints(self, x):
        self.write('SWE:POIN {}'.format(x))

    def SetAverages(self, navg):
        #self.write('AVER:TYPE RMS')   # Power averaging
        self.write('AVER:COUNT {}'.format(navg))
        if navg > 1:
            self.write(':TRAC:TYPE AVER')
        else:
            self.write(':TRAC:TYPE WRITE')

    def GetAverages(self):
        tracetype = self.query(':TRAC:TYPE?')
        if tracetype == 'AVER\n':
            navg = self.query('AVER:COUNT?')
            return float(navg)
        else:
            return 1

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

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass
