from stlab.devices.instrument import instrument
from stlab.utils.stlabdict import stlabdict as stlabdict
import numpy as np
import pandas as pd

import abc


def numtostr(mystr):
    return '%20.15e' % mystr


class basepna(instrument, abc.ABC):
    def __init__(self, addr, reset=True, verb=True):
        super().__init__(addr, reset, verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None
        self.id()
        if reset:
            self.SetContinuous(False)  #Turn off continuous mode

##### METHODS THAT CAN GENERALLY BE USED ON ALL PNAs.  REIMPLEMENT IF NECESSARY #######

    def SetContinuous(self, var=True):
        if var:
            self.write('INIT:CONT 1')  #Turn on continuous mode
        elif not var:
            self.write('INIT:CONT 0')  #Turn off continuous mode
        return

    def SetStart(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:STAR ' + mystr
        self.write(mystr)

    def SetEnd(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:STOP ' + mystr
        self.write(mystr)

    def SetCenter(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:CENT ' + mystr
        self.write(mystr)

    def SetSpan(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:SPAN ' + mystr
        self.write(mystr)

    def GetStart(self):
        mystr = 'SENS:FREQ:STAR?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def GetEnd(self):
        mystr = 'SENS:FREQ:STOP?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def GetCenter(self):
        mystr = 'SENS:FREQ:CENT?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def GetSpan(self):
        mystr = 'SENS:FREQ:SPAN?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def SetIFBW(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:BWID ' + mystr
        self.write(mystr)

    def GetIFBW(self):
        mystr = 'SENS:BWID?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def SetPower(self, x):
        mystr = numtostr(x)
        mystr = 'SOUR:POW ' + mystr
        self.write(mystr)

    def GetPower(self):
        mystr = 'SOUR:POW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def SetPoints(self, x):
        mystr = '%d' % x
        mystr = 'SENS:SWE:POIN ' + mystr
        self.write(mystr)

    def GetPoints(self):
        mystr = 'SENS:SWE:POIN?'
        pp = self.query(mystr)
        pp = int(pp)
        return pp

    def Trigger(self, block=True):
        if block:
            print((self.query('INIT;*OPC?')))
        else:
            self.write('INIT')
        return

    def SetPowerOff(self):
        self.write("SOUR1:POW1:MODE OFF")
        return

    def SetPowerOn(self):
        self.write("SOUR1:POW1:MODE ON")
        return

##### ABSTRACT METHODS TO BE IMPLEMENTED ON A PER PNA BASIS #####################

    @abc.abstractmethod
    def GetFrequency(self):
        freq = self.query('CALC:X?')
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        return freq

    @abc.abstractmethod
    def GetTraceNames(self):
        pars = self.query('CALC:PAR:CAT:EXT?')
        pars = pars.strip('\n').strip('"').split(',')
        parnames = pars[1::2]  #parameter names
        pars = pars[::2]  #parameter identifiers
        return pars, parnames

    @abc.abstractmethod
    def SetActiveTrace(self, mystr):
        self.write('CALC:PAR:SEL "%s"' % mystr)

    @abc.abstractmethod
    def GetTraceData(self):
        yy = self.query("CALC:DATA? SDATA")
        yy = np.asarray([float(xx) for xx in yy.split(',')])
        yyre = yy[::2]
        yyim = yy[1::2]
        return yyre, yyim

    @abc.abstractmethod
    def CalOn(self):
        mystr = "SENS:CORR ON"
        self.write(mystr)

    @abc.abstractmethod
    def CalOff(self):
        mystr = "SENS:CORR OFF"
        self.write(mystr)

    @abc.abstractmethod
    def GetCal(self):
        return bool(int(self.query('SENS:CORR?')))


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
