import visa
import numpy as np
import time
from stlab.devices.instrument import instrument
from collections import OrderedDict

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class RS_ZVB_pna(instrument):
    def __init__(self,addr='TCPIP::192.168.1.23::INSTR',reset=True,verb=True):
        super(type(self), self).__init__(addr,reset,verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None 
        self.id()
        self.twoportmode = False
        self.oneportmode = False
        self.DisplayOn()
        if reset:
            self.SetContinuous(False) #Turn off continuous mode
            self.TwoPort()
    def SinglePort(self):
        self.SetContinuous(False) #Turn off continuous mode
        self.ClearAll()
        tracenames = ['\'TrS11\'']
        tracevars = ['\'S11\'']
        for name,var in zip(tracenames,tracevars):
            self.write('CALC:PAR:SDEF ' + name + ', ' + var) #Set 2 traces and measurements
            self.write('DISP:WIND1:TRAC:EFE ' + name)
        self.twoportmode = False
        self.oneportmode = True
    def ClearAll(self):
        self.write('CALC:PAR:DEL:ALL') #Delete all traces (doesn't work on ZVB although it should)
    def Cleanup(self): #For some reason I can't delete default trace until other traces are added
        self.write("CALC:PAR:DEL 'Trc1'")
    def DisplayOn(self):
        self.write('SYST:DISP:UPD ON')
    def DisplayOff(self):
        self.write('SYST:DISP:UPD OFF')
    def TwoPort(self):
        self.SetContinuous(False) #Turn off continuous mode
        self.ClearAll()
        tracenames = ['\'TrS11\'','\'TrS21\'']
        tracevars = ['\'S11\'','\'S21\'']
        windows = ['1','2']
        for name,var,wind in zip(tracenames,tracevars,windows):
            self.write('DISP:WIND'+wind+':STAT ON')
            self.write('CALC:PAR:SDEF ' + name + ', ' + var) #Set 2 traces and measurements
            self.write('DISP:WIND'+wind+':TRAC:EFE ' + name)
        self.Cleanup()
        self.twoportmode = True
        self.oneportmode = False
    def SetRange(self,start,end):
        self.SetStart(start)
        self.SetEnd(end)
    def SetCenterSpan(self,center,span):
        self.SetCenter(center)
        self.SetSpan(span)
    def SetStart(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:STAR '+mystr
        self.write(mystr)
    def SetEnd(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:STOP '+mystr
        self.write(mystr)
    def SetCenter(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:CENT '+mystr
        self.write(mystr)
    def SetCWFreq(self,x):
        mystr = numtostr(x)
        mystr = 'SOUR:FREQ:CW '+mystr
        self.write(mystr)
    def SetSpan(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:SPAN '+mystr
        self.write(mystr)
    def SetIFBW(self,x):
        mystr = numtostr(x)
        mystr = 'BAND '+mystr
        self.write(mystr)
    def SetPower(self,x):
        mystr = numtostr(x)
        mystr = 'SOUR:POW '+mystr
        self.write(mystr)
    def GetPower(self):
        mystr = 'SOUR:POW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    def SetPoints(self,x):
        mystr = '%d' % x
        mystr = 'SWE:POIN '+mystr
        self.write(mystr)
    def SetTime(self,x):
        mystr = '%d' % x
        self.write('SWE:TIME ' + mystr)
        return
    def AutoscaleAll(self):
        pars = self.query('CALC:PAR:CAT?')
        pars = pars.strip('\n').strip("'").split(',')
        parnames = pars[1::2]
        pars = pars[::2]
        for ss in pars:
            self.write("DISP:WIND1:TRAC1:Y:AUTO ONCE '%s'" % ss)
    def Measure2ports(self,autoscale = True):
        if not self.twoportmode:
            self.TwoPort()
        self.Trigger() #Trigger single sweep and wait for response
        if autoscale:
            self.AutoscaleAll()
            #self.write('DISP:WIND1:TRAC:Y:AUTO ONCE') #Autoscale both traces
            #self.write('DISP:WIND2:TRAC:Y:AUTO ONCE')
        return self.GetAllData()
    def Measure1port(self,autoscale = True):
        pass
        if not self.oneportmode:
            self.SinglePort()
        self.Trigger() #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE') #Autoscale trace
        return self.GetAllData()
    def GetFrequency(self):
        freq = self.query('CALC:DATA:STIM?')
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        return freq
    def GetCWFreq(self):
        freq = self.query('SOUR:FREQ:CW?')
        freq = float(freq)
        return freq
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
    def LoadCal (self, calfile, channel = 1):
        mystr = "MMEM:LOAD:CORR " + str(channel) + ",'" + calfile + "'"
        self.write(mystr)
    def CalOn (self):
        mystr = "CORR ON"
        self.write(mystr)
    def CalOff (self):
        mystr = "CORR OFF"
        self.write(mystr)
    def GetCal(self): #Does not work on this PNA.  Always returns 1?
        return bool(int(self.query('CORR?')))
    def SetContinuous(self,bool=True):
        if bool:
            self.write('INIT:CONT 1') #Turn on continuous mode
        elif not bool:
            self.write('INIT:CONT 0') #Turn off continuous mode
    def Trigger(self,opc = True):
        if opc:
            print((self.query('INIT;*OPC?')))
        else:
            self.write('INIT')
        return



