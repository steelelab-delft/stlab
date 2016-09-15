import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class FieldfoxPNA(instrument):
    def __init__(self,addr='TCPIP::192.168.1.151::INSTR',reset=True,verb=True,mode='NA'):
        super(FieldfoxPNA, self).__init__(addr,reset,verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None 
        self.id()
        self.twoportmode = False
        if reset:
            if mode == 'NA':
                self.write('INST:SEL "NA"') #set mode to Network Analyzer
                self.write('INIT:CONT 0') #Turn off continuous mode
                self.TwoPort()
            elif mode == 'SA':
                self.write('INST:SEL "SA"') #set mode to Network Analyzer
                self.write('INIT:CONT 0') #Turn off continuous mode
    def SinglePort(self):
        self.write('CALC:PAR:COUN 1') #Set 1 trace and measurement
        self.write('CALC:PAR1:DEF S11')
        self.twoportmode = False
    def TwoPort(self):
        self.write('CALC:PAR:COUN 2') #Set 2 traces and measurements
        self.write('CALC:PAR1:DEF S11')
        self.write('CALC:PAR2:DEF S21')
        self.twoportmode = True
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
        if not self.twoportmode:
            self.TwoPort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND:TRAC1:Y:AUTO') #Autoscale both traces
            self.write('DISP:WIND:TRAC2:Y:AUTO')
        #Read measurement (in unicode strings)
        frec = self.query('FREQ:DATA?')
        self.write('CALC:PAR1:SEL')
        S11 = self.query('CALC:DATA:SDATA?')
        self.write('CALC:PAR2:SEL')
        S21 = self.query('CALC:DATA:SDATA?')
        #Convert to numpy arrays
        frec = np.array(list(map(float, frec.split(','))))
        S11 = np.array(list(map(float, S11.split(','))))
        S21 = np.array(list(map(float, S21.split(','))))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        S21re = S21[::2]  #Real part
        S21im = S21[1::2] #Imaginary part
        return (frec,S11re, S11im, S21re, S21im)
    def MeasureScreen(self):
        self.query('INIT:CONT 0;*OPC?')
        nmeas = self.query('CALC:PAR:COUN?')
        nmeas = int(nmeas)
        frec = self.query('FREQ:DATA?')
        frec = np.array(list(map(float, frec.split(','))))
        traces = []
        for i in range(1,nmeas+1):
            mystr = 'CALC:PAR' + ('%d' % i) + ':SEL'
            self.write(mystr)
            tr = self.query('CALC:DATA:SDATA?')
            tr = np.array(list(map(float, tr.split(','))))
            trre = tr[::2]  #Real part
            trim = tr[1::2] #Imaginary part
            traces.append(trre)
            traces.append(trim)
        result = []
        result.append(frec)
        result.append(np.ones(frec.size)*self.GetPower())
        for tt in traces:
            result.append(tt)
        result = np.transpose(np.asarray(result))
        return result
    def Measure1port(self,autoscale = True):
        if self.twoportmode:
            self.SinglePort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND:TRAC1:Y:AUTO') #Autoscale both traces
        #Read measurement (in unicode strings)
        frec = self.query('FREQ:DATA?')
        self.write('CALC:PAR1:SEL')
        S11 = self.query('CALC:DATA:SDATA?')
        #Convert to numpy arrays
        frec = np.array(list(map(float, frec.split(','))))
        S11 = np.array(list(map(float, S11.split(','))))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        return (frec,S11re,S11im)
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
