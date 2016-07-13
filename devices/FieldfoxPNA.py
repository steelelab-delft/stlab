import visa
import numpy as np

def numtostr(mystr):
    return '%12.8e' % mystr


class FieldfoxPNA:
    def __init__(self,addr='TCPIP::192.168.1.151::INSTR',reset=True,mode='NA'):
        self.rs = visa.ResourceManager('@py')
        self.pna = self.rs.open_resource(addr)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.pna.timeout = None 
        print(self.pna.query('*IDN?'))
        self.twoportmode = False
        if reset:
            self.pna.write('*RST')
            if mode == 'NA':
                self.pna.write('INST:SEL "NA"') #set mode to Network Analyzer
                self.pna.write('INIT:CONT 0') #Turn off continuous mode
                self.TwoPort()
            elif mode == 'SA':
                self.pna.write('INST:SEL "SA"') #set mode to Network Analyzer
                self.pna.write('INIT:CONT 0') #Turn off continuous mode
    def SinglePort(self):
        self.pna.write('CALC:PAR:COUN 1') #Set 1 trace and measurement
        self.pna.write('CALC:PAR1:DEF S11')
        self.twoportmode = False
    def TwoPort(self):
        self.pna.write('CALC:PAR:COUN 2') #Set 2 traces and measurements
        self.pna.write('CALC:PAR1:DEF S11')
        self.pna.write('CALC:PAR2:DEF S21')
        self.twoportmode = True
    def write(self,mystr):
        self.pna.write(mystr)
    def query(self,mystr):
        out = self.pna.query(mystr)
        return out
    def SetRange(self,start,end):
        self.SetStart(start)
        self.SetEnd(end)
    def SetCenterSpan(self,center,span):
        self.SetCenter(center)
        self.SetSpan(span)
    def SetStart(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:STAR '+mystr
        self.pna.write(mystr)
    def SetEnd(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:STOP '+mystr
        self.pna.write(mystr)
    def SetCenter(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:CENT '+mystr
        self.pna.write(mystr)
    def SetSpan(self,x):
        mystr = numtostr(x)
        mystr = 'FREQ:SPAN '+mystr
        self.pna.write(mystr)
    def SetIFBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:BWID '+mystr
        self.pna.write(mystr)
    def SetPower(self,x):
        mystr = numtostr(x)
        mystr = 'SOUR:POW '+mystr
        self.pna.write(mystr)
    def GetPower(self):
        mystr = 'SOUR:POW?'
        pp = self.pna.query(mystr)
        pp = float(pp)
        return pp
    def SetPoints(self,x):
        mystr = '%d' % x
        mystr = 'SWE:POIN '+mystr
        self.pna.write(mystr)
    def Measure2ports(self,autoscale = True):
        if not self.twoportmode:
            self.TwoPort()
        print(self.pna.query('INIT;*OPC?')) #Trigger single sweep and wait for response
        if autoscale:
            self.pna.write('DISP:WIND:TRAC1:Y:AUTO') #Autoscale both traces
            self.pna.write('DISP:WIND:TRAC2:Y:AUTO')
        #Read measurement (in unicode strings)
        frec = self.pna.query('FREQ:DATA?')
        self.pna.write('CALC:PAR1:SEL')
        S11 = self.pna.query('CALC:DATA:SDATA?')
        self.pna.write('CALC:PAR2:SEL')
        S21 = self.pna.query('CALC:DATA:SDATA?')
        #Convert to numpy arrays
        frec = np.array(map(float, frec.split(',')))
        S11 = np.array(map(float, S11.split(',')))
        S21 = np.array(map(float, S21.split(',')))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        S21re = S21[::2]  #Real part
        S21im = S21[1::2] #Imaginary part
        return (frec,S11re, S11im, S21re, S21im)
    def MeasureScreen(self):
        self.pna.query('INIT:CONT 0;*OPC?')
        nmeas = self.pna.query('CALC:PAR:COUN?')
        nmeas = int(nmeas)
        frec = self.pna.query('FREQ:DATA?')
        frec = np.array(map(float, frec.split(',')))
        traces = []
        for i in range(1,nmeas+1):
            mystr = 'CALC:PAR' + ('%d' % i) + ':SEL'
            self.pna.write(mystr)
            tr = self.pna.query('CALC:DATA:SDATA?')
            tr = np.array(map(float, tr.split(',')))
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
        print(self.pna.query('INIT;*OPC?')) #Trigger single sweep and wait for response
        if autoscale:
            self.pna.write('DISP:WIND:TRAC1:Y:AUTO') #Autoscale both traces
        #Read measurement (in unicode strings)
        frec = self.pna.query('FREQ:DATA?')
        self.pna.write('CALC:PAR1:SEL')
        S11 = self.pna.query('CALC:DATA:SDATA?')
        #Convert to numpy arrays
        frec = np.array(map(float, frec.split(',')))
        S11 = np.array(map(float, S11.split(',')))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        return (frec,S11re,S11im)
# DC source commands
    def EnableDCsource(self,reset=True):
        if reset:
            self.pna.write('SYST:VVS:VOLT 1.00')
        self.pna.write('SYST:VVS:ENAB 1')
        return
    def DisableDCsource(self):
        self.pna.write('SYST:VVS:ENAB 0')
        return
    def SetDCvoltage(self,vv):
	mystr = numtostr(vv)
        mystr = 'SYST:VVS:VOLT '+mystr
        self.pna.write(mystr)
	return
    def GetDCvoltage(self):
        mystr = 'SYST:VVS:VOLT?'
        vv = self.pna.query(mystr)
        vv = float(vv)
	return vv
    def GetMDCvoltage(self):
        mystr = 'SYST:VVS:MVOL?'
        vv = self.pna.query(mystr)
        vv = float(vv)
	return vv
    def GetDCcurrent(self):
        mystr = 'SYST:VVS:CURR?'
        vv = self.pna.query(mystr)
        vv = float(vv)
	return vv
#SA Mode commands
    def SetResBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:BAND:RES '+mystr
        self.pna.write(mystr)
    def SetVidBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:BAND:VID '+mystr
        self.pna.write(mystr)
    def SetCWFreq(self,x):
	mystr = numtostr(x)
	mystr = 'ISO:FREQ '+mystr
	self.pna.write(mystr)
    def SetCWPower(self,x):
        mystr = numtostr(x)
        mystr = 'ISO:POW '+mystr
        self.pna.write(mystr)
    def EnableIS(self):
        self.pna.write('ISO:ENAB 1')
    def DisableIS(self):
        self.pna.write('ISO:ENAB 0')
    def SetISmodeCW(self):
        self.pna.write('ISO:MODE CW')
    def SetInternalRef(self):
        self.pna.write('ROSC:SOUR INT')        
    def SetExternalRef(self):
        self.pna.write('ROSC:SOUR EXT')
    def MeasureSpectrum(self,autoscale = True):
        print(self.pna.query('INIT;*OPC?')) #Trigger single sweep and wait for response
        if autoscale:
            self.pna.write('DISP:WIND:TRAC:Y:AUTO') #Autoscale both traces
        #Read measurement (in unicode strings)
#        frec = self.pna.query('FREQ:DATA?')
        freqstart = float(self.pna.query('FREQ:STAR?'))
        freqstop = float(self.pna.query('FREQ:STOP?'))
        npoints =  float(self.pna.query('SWE:POIN?'))
        step = (freqstop-freqstart)/(npoints-1)
        frec = np.arange(freqstart,freqstop+step,step)
        spec = self.pna.query('TRAC:DATA?')
        #Convert to numpy arrays
        spec = np.asarray(map(float, spec.split(',')))
        return (frec,spec)    
