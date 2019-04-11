"""Module for instance of a Keysight N9010B EXA signal analyzer

This module contains the functions necessary to control and read data from 
a Keysight N9010B EXA signal analyzer. It inherits from basesa class.
"""

from stlab.devices.basesa import basesa
import numpy as np
import pandas as pd
import time


class Keysight_N9010B(basesa):
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

    def SetTraceAverageOn(self, ch=1):
        self.write(':TRAC{}:TYPE AVER'.format(ch))

    def SetTraceAverageOff(self, ch=1):
        self.write(':TRAC{}:TYPE WRIT'.format(ch))

    def SetAveragesType(self, avgtype):
        # Log-Pwr (Video), Pwr (RMS), Voltage
        self.write('AVER:TYPE ' + avgtype)

    def SetContinuous(self, state=True):
        if state:
            self.write('INIT:CONT 1')
        else:
            self.write('INIT:CONT 0')
        return

    def GetUnit(self):
        self.units = {
            'DBM': 'dBm',
            'DBMV': 'dBmV',
            'DBMA': 'dBmA',
            'V': 'V',
            'W': 'W',
            'A': 'A',
            'DBUV': 'dBuV',
            'DBUA': 'dBuA',
            'DBPW': 'dBpW',
            'DBUVM': 'dBuV/m',
            'DBUAM': 'dBuA/m',
            'DBPT': 'dBpT',
            'DBG': 'dBG'
        }
        aw = self.query(':UNIT:POW?')
        aw = aw.strip('\n')
        return self.units[aw]

    def SetUnit(self, unit):
        if unit.isupper():
            self.write(':UNIT:POW ' + unit)
        else:
            raise KeyError('Unknown unit!')

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

    def DisplayOn(self):
        mystr = ':DISP:ENAB ON'
        self.write(mystr)

    def DisplayOff(self):
        mystr = ':DISP:ENAB OFF'
        self.write(mystr)

    def MeasureIQ(self):
        self.SetContinuous(False)
        result = self.query(':READ:WAVeform0?')
        result = result.split(',')
        result = [float(x) for x in result]
        result = np.asarray(result)
        I = result[::2]
        Q = result[1::2]
        print('result length', type(result), len(result))
        print('I length', type(result), len(I))
        print('Q length', type(result), len(Q))
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
        measmode = self.GetMode()
        yunit = self.GetUnit()
        if measmode == 'SA':
            self.SetContinuous(False)
            self.write('INIT')
            # sleep for averaging time, otherwise timeout
            navg = self.GetAverages()
            tt = self.GetSweepTime()
            time.sleep(navg * tt)
            result = self.query('READ:SAN?')
            result = result.split(',')
            result = [float(x) for x in result]
            result = np.asarray(result)
            xvals = result[::2]
            yvals = result[1::2]
            output = pd.DataFrame()
            output['Frequency (Hz)'] = xvals
            output['Spectrum (' + yunit + ')'] = yvals
            return output