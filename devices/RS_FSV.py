"""Module for instance of a Rhode&Schwarz FSV Signal and Spectrum Analyzer

This module contains the functions necessary to control and read data from 
a Rhode&Schwarz FSV Signal and Spectrum Analyzer. It inherits from instrument class.
Note: This file is very rudimentary and needs enhancements for proper measurements, 
especially for compatibility with other stlab devices.
"""

from stlab.devices.instrument import instrument
from stlab.utils.stlabdict import stlabdict as stlabdict
import numpy as np
import pandas as pd


def num2str(num):
    return '%12.8e' % num


# Potential issues: some of the frequency commands require units, so 'Hz' might need to be added in some places
class RS_FSV(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.105::INSTR',
                 reset=False,
                 verb=True):
        super(RS_FSV, self).__init__(addr, reset, verb)

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

    def SetVideoBW(self, x):
        mystr = 'BAND:VID {}'.format(x)
        self.write(mystr)

    def GetVideoBW(self):
        mystr = 'BAND:VID?'
        x = self.query(mystr)
        return float(x)

    """
    def SetDigitalIFBW(self, x):
        mystr = 'WAV:DIF:BAND {}'.format(x)
        self.write(mystr)

    def GetDigitalIFBW(self):
        mystr = 'WAV:DIF:BAND?'
        x = self.query(mystr)
        return float(x)
    """

    def SetSampleRate(self, x):
        mystr = 'WAV:SRAT {}'.format(x)
        self.write(mystr)

    def GetSampleRate(self):
        mystr = 'WAV:SRAT?'
        x = self.query(mystr)
        return float(x)

    def SetPoints(self, npoints):
        self.write('SWE:POIN {}'.format(npoints))

    def SetAveragesType(self, avgtype):
        # VIDeo, LINear, POWer
        self.write('AVER:TYPE ' + avgtype)

    def SetAverages(self, navg):
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
            self.write('INIT:CONT ON')
        else:
            self.write('INIT:CONT OFF')
        return

    def SetMode(self, mode='SAN'):
        """
        change the instrument mode to one of the following:
        SAN (signal analyzer), IQ, ADEMOD (amplitude demodulation), NOIS (noise), PNO (phase noise)
        """

        self.write('INST:SEL ' + mode)
        return

    def SetReference(self, ref='INT'):
        # INT, EXT, EAUT
        self.write('ROSC:SOUR ' + ref)
        return

    def MeasureScreen(self, ch=1):
        # TODO
        self.SetContinuous(False)
        result = self.query('TRAC? TRACE{}'.format(ch))
        # TODO: What format does the data come in?
        result = result.split(',')
        result = [float(x) for x in result]
        result = np.asarray(result)
        xx = result[::2]
        yy = result[1::2]
        output = pd.DataFrame()
        output['Frequency (Hz)'] = xx
        output['PSD (dBm)'] = yy
        output['Res BW (Hz)'] = self.GetResolutionBW()
        return output

    def DisplayOn(self):
        self.write('SYST:DISP:UPD ON')

    def DisplayOff(self):
        self.write('SYST:DISP:UPD OFF')

    ### Functions below are old and deprecated
    def prepare_CW(self, CWsource_addr):
        """
        Initializing FSV with SMB100A for a CW measurement: VNA mode;
        Note that SMB100A needs to be connected;
        Also connect the clock of SMB100A to FSV. No TTL handshake yet;
        """

        self._CWsource = CWsource_addr
        self.reset()
        self.SetMode('SAN')  # Select signal analyzer mode
        self.SetContinuous(False)  # Turn off continuous sweep
        self.SetReference('EXT')  # sync FSV with generator
        # Configure external tracking generator: SMB100A RF source

        self.write('SYST:COMM:RDEV:GEN1:TYPE \'SMB100A12\'')  # generator type
        self.write('SYST:COMM:RDEV:GEN1:INT TCP')  # connection type
        self.write('SYST:COMM:TCP:RDEV:GEN1:ADDR ' +
                   self._CWsource)  # IP adress of generator
        self.write('SOUR:EXT1:ROSC INT')  # specify oscillator for generator

    def prepare_TD(self, LOsource_addr=None):
        """
        Prepare FSV for time domain measurement.
        Set external trigger.
        Use IQ aquisition mode
        """

        self._LOsource_addr = LOsource_addr
        self.reset()
        self.SetReference('EXT')  # sync FSV with generator
        self.write('SYST:COMM:RDEV:GEN1:TYPE \'SMB100A12\'')  # generator type
        self.write('SYST:COMM:RDEV:GEN1:INT TCP')  # connection type
        self.write('SYST:COMM:TCP:RDEV:GEN1:ADDR ' +
                   self._LOsource_addr)  # IP adress of generator
        self.write('SOUR:EXT1:ROSC INT')  # specify oscillator for generator

        # Configuring IQ mode
        self.SetMode('IQ')  # Select VSA mode, extraction of IQ
        self.write('TRIG:SOUR EXT')  # Set trigger to external AWG
        self.write('TRIG: POS')  # will trigger on positive slope to start
        # measurement
        self.write('INP:SEL RF')
        self.write('INP:GAIN:STAT ON')

    def measure_TD(self):
        data = self.query("TRAC:IQ:DATA?")
        return data

    def frequency_sweep(self, fstart, fstop):
        self.prepare_CW('192.168.1.25')
        self.write('SOUR:EXT1 ON')
        self._fstart = num2str(fstart)
        self._fstop = num2str(fstop)
        self.write('FREQ:STAR ' + self._fstart + 'Hz')
        self.write('SWE:POIN ' + num2str(1000))
        self.write('FREQ:STOP ' + self._fstop + 'Hz')

        self.write('SWE:COUN 10')
        self.write('AVER:STAT ON')
        self.write('INIT;*WAI')

        self.write('SOUR:EXT1 OFF')
        # extract data
        # TODO

    def frequency_power_sweep(self, fstart, fstop, fstep, pstart, pstop,
                              pstep):
        pass
        # TODO Write code for powersweep

    def set_CWsource(self, adrr):
        self._CWsource = adrr

    def set_LOsource(self, addr):
        self._LOsource = addr

    def set_CW_power(self, power):
        self._CWpower = num2str(power)
        self.write('SOUR:EXT1:POW ' + self._CWpower)

    def set_LO_power(self, power):
        self._LOpower = num2str(power)
        self.write('SOUR:EXT1:POW ' + self._LOpower)

    def set_LO_frequency(self, freq):
        self._LO_frequency = num2str(freq)
        self.write('FREQ:CENT ' + self._LO_frequency + ' Hz')

    def GetMetadataString(
            self
    ):  # Should return a string of metadata adequate to write to a file
        pass
