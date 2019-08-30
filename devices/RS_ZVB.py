"""Module for instance of a R&S ZVB vector network analyzer

This module contains the functions necessary to control and read data from 
a R&S ZVB vector network analyzer. It inherits from basepna class.

"""
import numpy as np
from stlab.devices.basepna import basepna
from stlabutils.utils.stlabdict import stlabdict


def numtostr(mystr):
    return '%20.15e' % mystr


#    return '%20.10f' % mystr


class RS_ZVB_pna(basepna):
    def __init__(self,
                 addr='TCPIP::192.168.1.23::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.twoportmode = False
        self.oneportmode = False
        self.DisplayOn()
        if reset:
            self.TwoPort()

#####  Reimplementation of some functions from basepna to accomodate differences

    def SetIFBW(self, x):
        mystr = numtostr(x)
        mystr = 'BAND ' + mystr
        self.write(mystr)

    def GetAllData(self):
        data = super(RS_ZVB_pna, self).GetAllData()
        #Check if a time sweep.  If so, replace column title "Frequency" with "Time"
        if 'XTIM' in self.query('FUNC?'):
            datasub = stlabdict([('Time (s)', v) if k == 'Frequency (Hz)' else
                                 (k, v) for k, v in d.items()])
            return datasub
        else:
            return data

##### ABSTRACT METHODS TO BE IMPLEMENTED ON A PER PNA BASIS #####################

    def GetFrequency(self):
        freq = self.query('CALC:DATA:STIM?')
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        return freq

    def GetTraceNames(self):
        pars = self.query('CALC:PAR:CAT?')
        pars = pars.strip('\n').strip("'").split(',')
        parnames = pars[1::2]  #parameter names
        pars = pars[::2]  #parameter identifiers
        return pars, parnames

    def SetActiveTrace(self, mystr):
        self.write('CALC:PAR:SEL "%s"' % mystr)

    def GetTraceData(self):
        yy = self.query("CALC:DATA? SDATA")
        yy = np.asarray([float(xx) for xx in yy.split(',')])
        yyre = yy[::2]
        yyim = yy[1::2]
        return yyre, yyim

    def CalOn(self):
        mystr = "CORR ON"
        self.write(mystr)

    def CalOff(self):
        mystr = "CORR OFF"
        self.write(mystr)

    def GetCal(
            self
    ):  #Does not work on this PNA.  Always returns 1? I manually return false
        #        return bool(int(self.query('CORR?')))
        return False


###  Optional methods

    def LoadCal(self, calfile, channel=1):
        mystr = "MMEM:LOAD:CORR " + str(channel) + ",'" + calfile + "'"
        self.write(mystr)

    def SetCWFreq(self, x):
        mystr = numtostr(x)
        mystr = 'SOUR:FREQ:CW ' + mystr

    def GetCWFreq(self):
        freq = self.query('SOUR:FREQ:CW?')
        freq = float(freq)
        return freq
        self.write(mystr)

    def SetTime(self, x):
        mystr = '%d' % x
        self.write('SWE:TIME ' + mystr)
        return

    def SinglePort(self):
        self.SetContinuous(False)  #Turn off continuous mode
        self.ClearAll()
        tracenames = ['\'TrS11\'']
        tracevars = ['\'S11\'']
        for name, var in zip(tracenames, tracevars):
            self.write('CALC:PAR:SDEF ' + name + ', ' +
                       var)  #Set 2 traces and measurements
            self.write('DISP:WIND1:TRAC:EFE ' + name)
        self.twoportmode = False
        self.oneportmode = True

    def ClearAll(self):
        self.write(
            'CALC:PAR:DEL:ALL'
        )  #Delete all traces (doesn't work on ZVB although it should)

    def Cleanup(
            self
    ):  #For some reason I can't delete default trace until other traces are added
        self.write("CALC:PAR:DEL 'Trc1'")

    def DisplayOn(self):
        self.write('SYST:DISP:UPD ON')

    def DisplayOff(self):
        self.write('SYST:DISP:UPD OFF')

    def TwoPort(self):
        self.SetContinuous(False)  #Turn off continuous mode
        self.ClearAll()
        tracenames = ['\'TrS11\'', '\'TrS21\'']
        tracevars = ['\'S11\'', '\'S21\'']
        windows = ['1', '2']
        for name, var, wind in zip(tracenames, tracevars, windows):
            self.write('DISP:WIND' + wind + ':STAT ON')
            self.write('CALC:PAR:SDEF ' + name + ', ' +
                       var)  #Set 2 traces and measurements
            self.write('DISP:WIND' + wind + ':TRAC:EFE ' + name)
        self.Cleanup()
        self.twoportmode = True
        self.oneportmode = False

    def AutoscaleAll(self):
        pars = self.query('CALC:PAR:CAT?')
        pars = pars.strip('\n').strip("'").split(',')
        parnames = pars[1::2]
        pars = pars[::2]
        for ss in pars:
            self.write("DISP:WIND1:TRAC1:Y:AUTO ONCE '%s'" % ss)

    def Measure2ports(self, autoscale=True):
        if not self.twoportmode:
            self.TwoPort()
        self.Trigger()  #Trigger single sweep and wait for response
        if autoscale:
            self.AutoscaleAll()
            #self.write('DISP:WIND1:TRAC:Y:AUTO ONCE') #Autoscale both traces
            #self.write('DISP:WIND2:TRAC:Y:AUTO ONCE')
        return self.GetAllData()

    def Measure1port(self, autoscale=True):
        pass
        if not self.oneportmode:
            self.SinglePort()
        self.Trigger()  #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE')  #Autoscale trace
        return self.GetAllData()

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass

    ''' Old routine before abclass
    def GetAllData(self):
        Cal = self.GetCal()
        Cal = False #Suppress uncalibrated return.  GetCal doesn't work anyway
        pars = self.query('CALC:PAR:CAT?')
        pars = pars.strip('\n').strip("'").split(',')
        parnames = pars[1::2]
        pars = pars[::2]
        if 'XTIM' in self.query('FUNC?'):
            names = ['Time (s)']
        else:
            names = ['Frequency (Hz)']
        alltrc = [self.GetFrequency()]
        for pp in parnames:
            names.append('%sre ()' % pp)
            names.append('%sim ()' % pp)
        if Cal:
            for pp in parnames:
                names.append('%sre unc ()' % pp)
                names.append('%sim unc ()' % pp)
        for par in pars:
            self.write("CALC:PAR:SEL '%s'" % par)
            yy = self.query("CALC:DATA? SDAT")
            yy = np.asarray([float(xx) for xx in yy.split(',')])
            yyre = yy[::2]
            yyim = yy[1::2]
            alltrc.append(yyre)
            alltrc.append(yyim)
        if Cal:
            for par in pars:
                self.write("CALC:PAR:SEL '%s'" % par)
                yy = self.query("CALC:DATA? SDAT")
                yy = np.asarray([float(xx) for xx in yy.split(',')])
                yyre = yy[::2]
                yyim = yy[1::2]
                alltrc.append(yyre)
                alltrc.append(yyim)
        final = OrderedDict()
        for name,data in zip(names,alltrc):
            final[name]=data
        return final
    '''
