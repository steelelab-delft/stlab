import visa
import numpy as np
import time

def numtostr(mystr):
    return '%12.8e' % mystr


class RS_ZND_pna:
    def __init__(self,addr='TCPIP::192.168.1.149::INSTR',reset=True):
        self.rs = visa.ResourceManager('@py')
        self.dev = self.rs.open_resource(addr)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None 
        print((self.query('*IDN?')))
        self.twoportmode = False
        self.oneportmode = False
        if reset:
            self.write('*RST')
 #           self.write('INIT:CONT 0') #Turn off continuous mode
            self.TwoPort()
    def SinglePort(self):
        self.write('CALC:PAR:DEL:ALL') #Delete default trace
        tracenames = ['\'TrS11\'']
        tracevars = ['\'S11\'']
        for name,var in zip(tracenames,tracevars):
            self.write('CALC:PAR:SDEF ' + name + ', ' + var) #Set 2 traces and measurements
            self.write('DISP:WIND1:TRAC:EFE ' + name)
        self.twoportmode = False
        self.oneportmode = True
    def TwoPort(self):
        self.write('CALC:PAR:DEL:ALL') #Delete default trace
        tracenames = ['\'TrS11\'','\'TrS21\'']
        tracevars = ['\'S11\'','\'S21\'']
        windows = ['1','2']
        for name,var,wind in zip(tracenames,tracevars,windows):
            self.write('DISP:WIND'+wind+':STAT ON')
            self.write('CALC:PAR:SDEF ' + name + ', ' + var) #Set 2 traces and measurements
            self.write('DISP:WIND'+wind+':TRAC1:FEED ' + name)
        self.twoportmode = True
        self.oneportmode = False
    def write(self,mystr):
        self.dev.write(mystr)
    def query(self,mystr,delay=None):
        out = self.dev.query(mystr,delay=delay)
        return out
    def read(self):
        out = self.dev.read()
        return out
    def SetMode(self,mode):
	self.write('FREQ:MODE '+str(mode)) #CW, FIX, SWE, SEGM
    def SetCWFreq(self,x):
	mystr = numtostr(x)
	mystr = 'FREQ:CW '+mystr
	self.write(mystr)
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
    def Measure2ports(self,autoscale = True):
        if not self.twoportmode:
            self.TwoPort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE') #Autoscale both traces
            self.write('DISP:WIND2:TRAC1:Y:AUTO ONCE')
        #Read measurement (in unicode strings)
        frec = self.query('CALC:DATA:STIM?')
        #self.write('CALC:PAR1:SEL')
        S11 = self.query('CALC:DATA:TRAC? \'TrS11\', SDAT')
        #self.write('CALC:PAR2:SEL')
        S21 = self.query('CALC:DATA:TRAC? \'TrS21\', SDAT')
        #Convert to numpy arrays
        frec = np.array(list(map(float, frec.split(','))))
        S11 = np.array(list(map(float, S11.split(','))))
        S21 = np.array(list(map(float, S21.split(','))))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        S21re = S21[::2]  #Real part
        S21im = S21[1::2] #Imaginary part
        return (frec,S11re, S11im, S21re, S21im)

    def Measure1port(self,autoscale = True):
        pass
        if not self.oneportmode:
            self.SinglePort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC1:Y:AUTO ONCE') #Autoscale trace
        #Read measurement (in unicode strings)
        frec = self.query('CALC:DATA:STIM?')
        S11 = self.query('CALC:DATA:TRAC? \'TrS11\', SDAT')
        #Convert to numpy arrays
        frec = np.array(list(map(float, frec.split(','))))
        S11 = np.array(list(map(float, S11.split(','))))
        S11re = S11[::2]  #Real part
        S11im = S11[1::2] #Imaginary part
        return (frec,S11re,S11im)
