"""Module for instance of a Rhode&Schwarz FSV Signal and Spectrum Analyzer

This module contains the functions necessary to control and read data from 
a Rhode&Schwarz FSV Signal and Spectrum Analyzer. It inherits from basesa class.
"""

from .basesa import basesa
import numpy as np
import pandas as pd
import time


def num2str(num):
    return '%12.8e' % num


# Potential issues: some of the frequency commands require units, so 'Hz' might need to be added in some places
class RS_FSV(basesa):
    def __init__(self,
                 addr='TCPIP::192.168.1.216::INSTR',
                 reset=True,
                 verb=True):
      
        super().__init__(addr, reset, verb)
        self.dev.timeout = None

    def SetInputAtt(self, att=10):
        self.write('INP:ATT {} dB'.format(att))

    def GetInputAtt(self):
        inputatt = self.query('INP:ATT?')
        return float(inputatt)

    def SetTraceOn(self, ch=1):
        self.write('DISP:TRAC{} ON'.format(ch))

    def SetTraceOff(self, ch=1):
        self.write('DISP:TRAC{} OFF'.format(ch))

    def SetTraceAverageOn(self, ch=1):
        self.write('DISP:TRAC{}:MODE AVER'.format(ch))

    def SetTraceAverageOff(self, ch=1):
        self.write('DISP:TRAC{}:MODE WRIT'.format(ch))

    def SetAveragesType(self, avgtype):
        # VIDeo, LINear, POWer
        self.write('AVER:TYPE ' + avgtype)

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

    def GetUnit(self):
        self.units = {
            'DBM': 'dBm',
            'V': 'V',
            'A': 'A',
            'W': 'W',
            'DBPW': 'dBpW',
            'WATT': 'W',
            'DBUV': 'dBuV',
            'DBMV': 'dBmV',
            'VOLT': 'V',
            'DBUA': 'dBuA',
            'AMP': 'A'
        }
        aw = self.query('CALC:UNIT:POW?')
        aw = aw.strip('\n')
        return self.units[aw]

    def SetUnit(self, unit):
        if unit.isupper():
            self.write('CALC:UNIT:POW ' + unit)
        else:
            raise KeyError('Unknown unit!')

    def MarkerOff(self, mk='all'):
        if mk == 'all':
            self.write('CALC:MARK:AOFF')
        else:
            for m in mk:
                self.write('CALC:MARK{} OFF'.format(m))

    def MarkerOn(self, mk):
        for m in mk:
            self.write('CALC:MARK{} ON'.format(m))

    def SetMarkerFreq(self, mk, freq):
        for m, f in zip(mk, freq):
            self.write('CALC:MARK{}:X {}Hz'.format(m, f))

    def GetMarkerAmpt(self, mk):
        aw = float(self.query('CALC:MARK{}:Y?'.format(mk)))
        return aw

    def GetMarkerNoise(self, mk):
        self.write('CALC:MARK{}:FUNC:NOIS ON'.format(mk))
        aw = float(self.query('CALC:MARK{}:FUNC:NOIS:RES?'.format(mk)))
        return aw

    def GetMarkerBandPowerDensity(self, mk, bw):
        self.write('CALC:MARK{}:FUNC:BPOW:STAT ON'.format(mk))
        self.write('CALC:MARK{}:FUNC:BPOW:MODE DENS'.format(mk))
        self.write('CALC:MARK{}:FUNC:BPOW:SPAN {}Hz'.format(mk, bw))
        aw = float(self.query('CALC:MARK{}:FUNC:BPOW:RES?').format(mk))
        return aw

    def DisplayOn(self):
        self.write('SYST:DISP:UPD ON')

    def DisplayOff(self):
        self.write('SYST:DISP:UPD OFF')

    def GetAverages(self):
        count = float(self.query(':SWE:COUN?'))
        return count

    def MeasureScreen(self, ch=1):
        measmode = self.GetMode()
        yunit = self.GetUnit()
        if measmode == 'SAN':
            self.SetContinuous(False)
            self.write('INIT')
            # sleep for averaging time, otherwise timeout
            navg = self.GetAverages()
            tt = self.GetSweepTime()
            sleeptime = navg * tt
            print('Measurement in progress. Waiting for {}s'.format(sleeptime))
            time.sleep(sleeptime)
            xvals = self.query('TRAC:DATA:X? TRACE{}'.format(ch))
            yvals = self.query('TRAC? TRACE{}'.format(ch))
            xvals = np.array([float(x) for x in xvals.split(',')])
            yvals = np.array([float(x) for x in yvals.split(',')])
            output = pd.DataFrame()
            output['Frequency (Hz)'] = xvals
            output['Spectrum (' + yunit + ')'] = yvals
            return output
        else:
            return KeyError('Instrument mode unknown!')

    ############################## For IQ measurements

    def SetDigitalIFBW(self, x):
        mystr = 'WAV:DIF:BAND {}'.format(x)
        self.write(mystr)

    def GetDigitalIFBW(self):
        mystr = 'WAV:DIF:BAND?'
        x = self.query(mystr)
        return float(x)

    ############################## Functions below are old and deprecated
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
