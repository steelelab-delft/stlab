"""Module implementing basic Signal and Spectrum Analyzer

This module is the base class for most SAs
"""

from stlab.devices.instrument import instrument
from stlab.utils.stlabdict import stlabdict as stlabdict
import numpy as np
import pandas as pd

import abc


def numtostr(mystr):
    return '%20.15e' % mystr


class basesaa(instrument, abc.ABC):
    def __init__(self, addr, reset, verb):
        super().__init__(addr, reset, verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None
        self.id()
        if reset:
            self.SetContinuous(False)  #Turn off continuous mode

##### METHODS THAT CAN GENERALLY BE USED ON ALL SAs.  REIMPLEMENT IF NECESSARY #######

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

    def SetSweepTime(self, tt):
        self.write('SWE:TIME {}'.format(tt))

    def GetSweepTime(self):
        tt = self.query('SWE:TIME?')
        return float(tt)

    def SetSampleRate(self, x):
        mystr = 'WAV:SRAT {}'.format(x)
        self.write(mystr)

    def GetSampleRate(self):
        mystr = 'WAV:SRAT?'
        x = self.query(mystr)
        return float(x)

    def SetPoints(self, npoints):
        self.write('SWE:POIN {}'.format(npoints))

    def GetPoints(self):
        npts = self.query('SWE:POIN?')
        return float(npts)

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
    
    def GetAveragesType(self):
        avgtype = self.query('AVER:TYPE?')
        return avgtype

    def GetMode(self):
        aw = self.query('INST:SEL?')
        return aw.strip('\n')
    
    def SetReference(self, ref='INT'):
        # INT, EXT, EAUT
        self.write('ROSC:SOUR ' + ref)
        return
    
    def GetReference(self):
        aw = self.query('ROSC:SOUR?')
        return aw.strip('\n')

    def GetMetadataString(self):
        # Should return a string of metadata adequate to write to a file
        pass
    
    def GetSweepTime(self):
        sweeptime = self.query('SWE:TIME?')
        return float(sweeptime)
    

##### ABSTRACT METHODS TO BE IMPLEMENTED ON A PER PNA BASIS #####################

    @abc.abstractmethod
    def SetInputAtt(self, att=10):
        self.write('INP:ATT {} dB'.format(att))

    @abc.abstractmethod
    def GetInputAtt(self):
        inputatt = self.query('INP:ATT?')
        return float(inputatt)

    @abc.abstractmethod
    def SetTraceAverageOn(self, ch=1):
        self.write('DISP:TRAC{}:MODE AVER'.format(ch))

    @abc.abstractmethod
    def SetTraceAverageOff(self, ch=1):
        self.write('DISP:TRAC{}:MODE WRIT'.format(ch))

    @abc.abstractmethod
    def SetTraceOn(self, ch=1):
        self.write('DISP:TRAC{} ON'.format(ch))

    @abc.abstractmethod
    def SetTraceOff(self, ch=1):
        self.write('DISP:TRAC{} OFF'.format(ch))

    @abc.abstractmethod
    def SetAveragesType(self, avgtype):
        # VIDeo, LINear, POWer
        self.write('AVER:TYPE ' + avgtype)

    @abc.abstractmethod
    def GetAveragesType(self):
        avgtype = self.query('AVER:TYPE?')
        return avgtype

    @abc.abstractmethod
    def SetDigitalIFBW(self, x):
        mystr = 'WAV:DIF:BAND {}'.format(x)
        self.write(mystr)

    @abc.abstractmethod
    def GetDigitalIFBW(self):
        mystr = 'WAV:DIF:BAND?'
        x = self.query(mystr)
        return float(x)

    @abc.abstractmethod
    def SetSampleRate(self, x):
        mystr = 'WAV:SRAT {}'.format(x)
        self.write(mystr)

    @abc.abstractmethod
    def GetSampleRate(self):
        mystr = 'WAV:SRAT?'
        x = self.query(mystr)
        return float(x)

    @abc.abstractmethod
    def SetIQSweepTime(self, x):
        mystr = 'WAVeform:SWEep:TIME {}'.format(x)
        self.write(mystr)

    @abc.abstractmethod
    def GetIQSweepTime(self):
        mystr = 'WAVeform:SWEep:TIME?'
        x = self.query(mystr)
        return float(x)
    
    @abc.abstractmethod
    def SetAveragesType(self, avgtype):
        # VIDeo, LINear, POWer
        self.write('AVER:TYPE ' + avgtype)
    
    @abc.abstractmethod
    def SetContinuous(self, state=True):
        if state:
            self.write('INIT:CONT ON')
        else:
            self.write('INIT:CONT OFF')
        return
    
    @abc.abstractmethod
    def SetMode(self, mode='SAN'):
        """
        change the instrument mode to one of the following:
        SAN (signal analyzer), IQ, ADEMOD (amplitude demodulation), NOIS (noise), PNO (phase noise)
        """
        self.write('INST:SEL ' + mode)
        return
    
    @abc.abstractmethod
    def MarkerOff(self, mk='all'):
        if mk == 'all':
            self.write('CALC:MARK:AOFF')
        else:
            for m in mk:
                self.write('CALC:MARK{} OFF'.format(m))

    @abc.abstractmethod
    def MarkerOn(self, mk):
        for m in mk:
            self.write('CALC:MARK{} ON'.format(m))

    @abc.abstractmethod
    def SetMarkerFreq(self, mk, freq):
        for m, f in zip(mk, freq):
            self.write('CALC:MARK{}:X {}Hz'.format(m, f))

    @abc.abstractmethod
    def GetMarkerAmpt(self, mk):
        aw = float(self.query('CALC:MARK{}:Y?'.format(mk)))
        return aw

    @abc.abstractmethod
    def GetMarkerNoise(self, mk):
        self.write('CALC:MARK{}:FUNC:NOIS ON'.format(mk))
        aw = float(self.query('CALC:MARK{}:FUNC:NOIS:RES?'.format(mk)))
        return aw

    @abc.abstractmethod
    def GetMarkerBandPowerDensity(self, mk, bw):
        self.write('CALC:MARK{}:FUNC:BPOW:STAT ON'.format(mk))
        self.write('CALC:MARK{}:FUNC:BPOW:MODE DENS'.format(mk))
        self.write('CALC:MARK{}:FUNC:BPOW:SPAN {}Hz'.format(mk, bw))
        aw = float(self.query('CALC:MARK{}:FUNC:BPOW:RES?').format(mk))
        return aw

    @abc.abstractmethod
    def DisplayOn(self):
        self.write('SYST:DISP:UPD ON')

    @abc.abstractmethod
    def DisplayOff(self):
        self.write('SYST:DISP:UPD OFF')


##### FULLY IMPLEMENTED METHODS THAT DO NOT NEED TO BE REIMPLEMENTED (BUT CAN BE IF NECESSARY) #####################

    def SetRange(self, start, end):
        self.SetStart(start)
        self.SetEnd(end)

    def SetCenterSpan(self, center, span):
        self.SetCenter(center)
        self.SetSpan(span)

    def GetAllData(self, keep_uncal=True):
        pars, parnames = self.GetTraceNames()
        self.SetActiveTrace(pars[0])
        names = ['Frequency (Hz)']
        alltrc = [self.GetFrequency()]
        for pp in parnames:
            names.append('%sre ()' % pp)
            names.append('%sim ()' % pp)
            names.append('%sdB (dB)' % pp)
            names.append('%sPh (rad)' % pp)
        for par in pars:
            self.SetActiveTrace(par)
            yyre, yyim = self.GetTraceData()
            alltrc.append(yyre)
            alltrc.append(yyim)
            yydb = 20. * np.log10(np.abs(yyre + 1j * yyim))
            yyph = np.unwrap(np.angle(yyre + 1j * yyim))
            alltrc.append(yydb)
            alltrc.append(yyph)
        Cal = self.GetCal()
        if Cal and keep_uncal:
            for pp in parnames:
                names.append('%sre unc ()' % pp)
                names.append('%sim unc ()' % pp)
                names.append('%sdB unc (dB)' % pp)
                names.append('%sPh unc (rad)' % pp)
            self.CalOff()
            for par in pars:
                self.SetActiveTrace(par)
                yyre, yyim = self.GetTraceData()
                alltrc.append(yyre)
                alltrc.append(yyim)
                yydb = 20. * np.log10(np.abs(yyre + 1j * yyim))
                yyph = np.unwrap(np.angle(yyre + 1j * yyim))
                alltrc.append(yydb)
                alltrc.append(yyph)
            self.CalOn()
        final = stlabdict()
        for name, data in zip(names, alltrc):
            final[name] = data
        final.addparcolumn('Power (dBm)', self.GetPower())
        return final

    def MeasureScreen(self, keep_uncal=True, N_averages=1):
        self.SetContinuous(False)
        if N_averages == 1:
            self.Trigger()  #Trigger single sweep and wait for response
        elif N_averages > 1:
            self.write('SENS:AVER:COUN %d' % N_averages)
            self.write('SENS:AVER ON')
            self.write('SENS:AVER:CLEAR')
            naver = int(self.query('SENS:AVER:COUN?'))
            for _ in range(naver):
                self.Trigger()
                # self.AutoScaleAll()
            self.write('SENS:AVER OFF')
        return self.GetAllData(keep_uncal)

    def GetAllData_pd(self, keep_uncal=True):
        pars, parnames = self.GetTraceNames()
        self.SetActiveTrace(pars[0])
        names = ['Frequency (Hz)']
        alltrc = [self.GetFrequency()]
        for pp in parnames:
            names.append('%sre ()' % pp)
            names.append('%sim ()' % pp)
            names.append('%sdB (dB)' % pp)
            names.append('%sPh (rad)' % pp)
        for par in pars:
            self.SetActiveTrace(par)
            yyre, yyim = self.GetTraceData()
            alltrc.append(yyre)
            alltrc.append(yyim)
            yydb = 20. * np.log10(np.abs(yyre + 1j * yyim))
            yyph = np.unwrap(np.angle(yyre + 1j * yyim))
            alltrc.append(yydb)
            alltrc.append(yyph)
        Cal = self.GetCal()
        if Cal and keep_uncal:
            for pp in parnames:
                names.append('%sre unc ()' % pp)
                names.append('%sim unc ()' % pp)
                names.append('%sdB unc (dB)' % pp)
                names.append('%sPh unc (rad)' % pp)
            self.CalOff()
            for par in pars:
                self.SetActiveTrace(par)
                yyre, yyim = self.GetTraceData()
                alltrc.append(yyre)
                alltrc.append(yyim)
                yydb = 20. * np.log10(np.abs(yyre + 1j * yyim))
                yyph = np.unwrap(np.angle(yyre + 1j * yyim))
                alltrc.append(yydb)
                alltrc.append(yyph)
            self.CalOn()

        final = pd.DataFrame()
        for name, data in zip(names, alltrc):
            final[name] = data
        final['Power (dBm)'] = self.GetPower()
        return final

    def MeasureScreen_pd(self, keep_uncal=True):
        self.SetContinuous(False)
        print(self.Trigger())  #Trigger single sweep and wait for response
        return self.GetAllData_pd(keep_uncal)

    '''
    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        result = self.id().strip() + '\n'
        result += 'Range = [{}, {}] Hz'.format(self.GetStart(),self.GetEnd()) + '\n'
        result += 'IFBW = {} Hz'.format(self.GetIFBW()) + '\n'
        result += 'Power = {} dBm'.format(self.GetPower()) + '\n'
        result += 'Npoints = {}'.format(self.GetPoints()) + '\n'
        result += 'Traces = {}'.format(self.GetTraceNames()[1]) + '\n'
        return result
    '''

    def MetaGetters(self):
        getters = [
            method_name for method_name in dir(self)
            if callable(getattr(self, method_name))
            if method_name.startswith('Get')
        ]
        getters.remove('GetAllData')
        getters.remove('GetAllData_pd')
        getters.remove('GetMetadataString')
        getters.remove('GetFrequency')
        getters.remove('GetTraceData')

        return getters
