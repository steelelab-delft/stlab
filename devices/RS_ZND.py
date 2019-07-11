"""Module for instance of a R&S ZND vector network analyzer

This module contains the functions necessary to control and read data from 
a R&S ZND vector network analyzer. It inherits from basepna class.

"""
import numpy as np
from stlab.devices.basepna import basepna


def numtostr(mystr):
    return '%20.15e' % mystr


#    return '%20.10f' % mystr


class RS_ZND(basepna):
    def __init__(self,
                 addr='TCPIP::192.168.1.149::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.twoportmode = False
        self.oneportmode = False
        if reset:
            self.TwoPort()



### REIMPLEMENTATION OF GENERIC FUNCTIONS

    def Reset(self):
        self.write('*RST')

    def SetContinuous(self,bool):
        if bool:
            self.write('INIT:CONT ON')
        elif not bool:
            self.write('INIT:CONT OFF')

    def SetIFBW(self, x):
        mystr = numtostr(x)
        mystr = 'BAND ' + mystr
        self.write(mystr)

## OBLIGATORY ABSTRACT METHODS TO BE IMPLEMENTED

    def GetFrequency(self):
        freq = self.query('CALC:DATA:STIM?')
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        return freq

    def GetTraceNames(self):
        pars = self.query('CALC:PAR:CAT?')
        pars = pars.strip('\n').strip("'").split(',')
        parnames = pars[1::2]
        pars = pars[::2]
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

    def GetCal(self):
        return bool(int(self.query('CORR?')))


## Optional methods

    ''' OLD METHOD BEFORE ABCLASS
    def GetAllData(self):
        Cal = self.GetCal()
        pars = self.query('CALC:PAR:CAT?')
        pars = pars.strip('\n').strip("'").split(',')
        parnames = pars[1::2]
        pars = pars[::2]
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
            yy = self.query("CALC:DATA:TRAC? '%s', SDAT" % par)
            yy = np.asarray([float(xx) for xx in yy.split(',')])
            yyre = yy[::2]
            yyim = yy[1::2]
            alltrc.append(yyre)
            alltrc.append(yyim)
        if Cal:
            for par in pars:
                yy = self.query("CALC:DATA:TRAC? '%s', NCD" % par)
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

    def LoadCal(self, calfile, channel=1):
        mystr = "MMEM:LOAD:CORR " + str(channel) + ",'" + calfile + "'"
        self.write(mystr)

    def SinglePort(self,tr='S11'):
        self.SetContinuous(False)  #Turn off continuous mode
        self.write('CALC:PAR:DEL:ALL')  #Delete default trace
        tracenames = ['\'Tr'+tr+'\'']
        tracevars = ['\''+tr+'\'']
        for name, var in zip(tracenames, tracevars):
            self.write('CALC:PAR:SDEF ' + name + ', ' +
                       var)  #Set 2 traces and measurements
            self.write('DISP:WIND1:TRAC:EFE ' + name)
        self.twoportmode = False
        self.oneportmode = True

    def TwoPort(self):
        self.SetContinuous(False)  #Turn off continuous mode
        self.write('CALC:PAR:DEL:ALL')  #Delete default trace
        tracenames = ['\'TrS11\'', '\'TrS21\'']
        tracevars = ['\'S11\'', '\'S21\'']
        windows = ['1', '2']
        for name, var, wind in zip(tracenames, tracevars, windows):
            self.write('DISP:WIND' + wind + ':STAT ON')
            self.write('CALC:PAR:SDEF ' + name + ', ' +
                       var)  #Set 2 traces and measurements
            self.write('DISP:WIND' + wind + ':TRAC1:FEED ' + name)
        self.twoportmode = True
        self.oneportmode = False

    def AutoScale(self):
        self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE')
        return

    def Measure2ports(self, autoscale=True):
        if not self.twoportmode:
            self.TwoPort()
        self.Trigger()  #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE')  #Autoscale both traces
            self.write('DISP:WIND2:TRAC1:Y:AUTO ONCE')
        return self.GetAllData()

    def Measure1port(self, autoscale=True):
        pass
        if not self.oneportmode:
            self.SinglePort()
        self.Trigger()  #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE')  #Autoscale trace
        return self.GetAllData()

    #To set different sweep types
    def SetSweepType(
            self, mystr
    ):  #Possible values: LINear | LOGarithmic | POWer | CW | POINt | SEGMent  (Default value is LINear)
        self.write('SENS:SWE:TYPE %s' % mystr)
        return

    def SetCWfrequency(self, xx):
        self.write('SENS:FREQ {}'.format(xx))
        return

    def ClearAll(self):
        self.write('CALC:PAR:DEL:ALL')

        
""" # Already implemented in basepna

        def SetSweepfrequency(self, start_freq, stop_freq, sweep_points): 
            self.write('SENS:FREQ:STAR {}GHZ'.format(start_freq))
            self.write('SENS:FREQ:STOP {}GHZ'.format(stop_freq))
            self.write('SWE:POIN {}'.format(sweep_points))
             
    
        def SetAverageSweeps(self, count): #Defines the number of consecutive sweeps to be combined for the sweep average ("Factor" ).
            self.write('SENS:AVER:COUN {}; :AVER ON'.format(count))
    
        def Initiate(self): #Starts a new single sweep sequence in all channels
            self.write('INIT:ALL') 
    
        def SetPower (self, x):
            self.write('SOUR:POW {}'.format(x))
    
        def SetSweepTime(self,x):
            self.write('SENS:SWE:TIME {}'.format(x))
             
        
"""    
