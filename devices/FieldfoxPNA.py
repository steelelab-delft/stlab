import visa
import numpy as np
from stlab.devices.instrument import instrument
from collections import OrderedDict

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class FieldfoxPNA(instrument):
    def __init__(self,addr='TCPIP::192.168.1.151::INSTR',reset=True,verb=True,mode='NA'):
        super(FieldfoxPNA, self).__init__(addr,reset,verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None 
        self.id()
        if reset:
            if mode == 'NA':
                self.write('INST:SEL "NA"') #set mode to Network Analyzer
                self.SetContinuous(False) #Turn off continuous mode
                self.TwoPort()
            elif mode == 'SA':
                self.write('INST:SEL "SA"') #set mode to Spectrum Analyzer
                self.SetContinuous(False)
    def SinglePort(self):
        self.write('CALC:PAR:COUN 1') #Set 1 trace and measurement
        self.write('CALC:PAR1:DEF S11')
    def TwoPort(self):
        self.write('CALC:PAR:COUN 2') #Set 2 traces and measurements
        self.write('CALC:PAR1:DEF S11')
        self.write('CALC:PAR2:DEF S21')
    '''
    def write(self,mystr):
        self.write(mystr)
    def query(self,mystr):
        out = self.query(mystr)
        return out
    '''
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
    def SetSpan(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:SPAN '+mystr
        self.write(mystr)
    def SetIFBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:BWID '+mystr
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
    def Measure2ports(self,autoscale = True):
        self.TwoPort()
        self.Trigger()
        if autoscale:
            self.write('DISP:WIND:TRAC1:Y:AUTO') #Autoscale both traces
            self.write('DISP:WIND:TRAC2:Y:AUTO') #Autoscale both traces
        return self.GetAllData()
    def GetAllData(self):
        Cal = self.GetCal()
        nmeas = self.query('CALC:PAR:COUN?')
        nmeas = int(nmeas)
        print(nmeas)
        pars = [self.query('CALC:PAR' + str(i+1) + ':DEF?').strip('\n') for i in range(0,nmeas)]
        print(pars)
        names = ['Frequency (Hz)']
        alltrc = [self.GetFrequency()]
        for pp in pars:
            names.append('%sre ()' % pp)
            names.append('%sim ()' % pp)
        if Cal:
            for pp in pars:
                names.append('%sre unc ()' % pp)
                names.append('%sim unc ()' % pp)
        for i in range(0,nmeas):
            self.write('CALC:PAR' + str(i+1) + ':SEL')
            yy = self.query('CALC:DATA:SDATA?')
            yy = np.asarray([float(xx) for xx in yy.split(',')])
            yyre = yy[::2]
            yyim = yy[1::2]
            alltrc.append(yyre)
            alltrc.append(yyim)
        if Cal:
            self.CalOff()
            for i in range(0,nmeas):
                self.write('CALC:PAR' + str(i+1) + ':SEL')
                yy = self.query('CALC:DATA:SDATA?')
                yy = np.asarray([float(xx) for xx in yy.split(',')])
                yyre = yy[::2]
                yyim = yy[1::2]
                alltrc.append(yyre)
                alltrc.append(yyim)
            self.CalOn()
        final = OrderedDict()
        for name,data in zip(names,alltrc):
            final[name]=data
        return final
    def MeasureScreen(self):
        self.Trigger()
        return self.GetAllData()
    def Measure1port(self,autoscale = True):
        self.SinglePort()
        self.Trigger()
        if autoscale:
            self.write('DISP:WIND:TRAC1:Y:AUTO') #Autoscale both traces
        return self.GetAllData()

    def LoadState (self, statefile):
        mystr = 'MMEM:LOAD:STAT "%s"' % statefile
        self.write(mystr)
    def CalOn (self):
        mystr = "CORR:USER 1"
        self.write(mystr)
    def CalOff (self):
        mystr = "CORR:USER 0"
        self.write(mystr)
    def GetCal(self):
        return bool(int(self.query('CORR:USER?')))
    def SetContinuous(self,bool=True):
        if bool:
            self.write('INIT:CONT 1') #Turn on continuous mode
        elif not bool:
            self.write('INIT:CONT 0') #Turn off continuous mode
    def Trigger(self):
        print((self.query('INIT;*OPC?')))
        return
    def GetFrequency(self):
        frec = self.query('FREQ:DATA?')
        #Convert to numpy arrays
        frec = np.array(list(map(float, frec.split(','))))
        return frec

# DC source commands
    def EnableDCsource(self,reset=True):
        if reset:
            self.write('SYST:VVS:VOLT 1.00')
        self.write('SYST:VVS:ENAB 1')
        return
    def DisableDCsource(self):
        self.write('SYST:VVS:ENAB 0')
        return
    def SetDCvoltage(self,vv):
        mystr = numtostr(vv)
        mystr = 'SYST:VVS:VOLT '+mystr
        self.write(mystr)
        return
    def GetDCvoltage(self):
        mystr = 'SYST:VVS:VOLT?'
        vv = self.query(mystr)
        vv = float(vv)
        return vv
    def GetMDCvoltage(self):
        mystr = 'SYST:VVS:MVOL?'
        vv = self.query(mystr)
        vv = float(vv)
        return vv
    def GetDCcurrent(self):
        mystr = 'SYST:VVS:CURR?'
        vv = self.query(mystr)
        vv = float(vv)
        return vv

#SA Mode commands
    def SetResBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:BAND:RES '+mystr
        self.write(mystr)
    def SetVidBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:BAND:VID '+mystr
        self.write(mystr)
    def SetCWFreq(self,x):
        mystr = numtostr(x)
        mystr = 'ISO:FREQ '+mystr
        self.write(mystr)
    def SetCWPower(self,x):
        mystr = numtostr(x)
        mystr = 'ISO:POW '+mystr
        self.write(mystr)
    def EnableIS(self):
        self.write('ISO:ENAB 1')
    def DisableIS(self):
        self.write('ISO:ENAB 0')
    def SetISmodeCW(self):
        self.write('ISO:MODE CW')
    def SetInternalRef(self):
        self.write('ROSC:SOUR INT')        
    def SetExternalRef(self):
        self.write('ROSC:SOUR EXT')
    def MeasureSpectrum(self,autoscale = True):
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND:TRAC:Y:AUTO') #Autoscale both traces
        #Read measurement (in unicode strings)
#        frec = self.query('FREQ:DATA?')
        freqstart = float(self.query('FREQ:STAR?'))
        freqstop = float(self.query('FREQ:STOP?'))
        npoints =  float(self.query('SWE:POIN?'))
        step = (freqstop-freqstart)/(npoints-1)
        frec = np.arange(freqstart,freqstop+step,step)
        spec = self.query('TRAC:DATA?')
        #Convert to numpy arrays
        spec = np.asarray(list(map(float, spec.split(','))))
        return (frec,spec)

