import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class PNAN5222A(instrument):
    def __init__(self,addr='TCPIP::192.168.1.151::INSTR',reset=True,verb=True):
        super(PNAN5222A, self).__init__(addr,reset,verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None 
        self.id()
        self.twoportmode = False
        if reset:
            self.write('INIT:CONT 0') #Turn off continuous mode
            self.TwoPort()
    def SinglePort(self):
        windows = self.query('DISP:CAT?')
        windows = windows.strip('\n')
        print(windows == '"EMPTY"')
        if windows != '"EMPTY"':
            windows = [int(x) for x in windows.strip('"').split(',')]
            for i in windows:
                self.write('DISP:WIND%d OFF' % i)
        self.write('DISP:WIND1 ON')
        tracenames = ['CH1_S11']
        measnames = ['S11']
        for i,(meas,trc) in enumerate(zip(measnames,tracenames)):
            self.write("CALC:PAR:DEF:EXT '%s', '%s'" % (trc,meas))
            self.write("DISP:WIND:TRAC%d:FEED '%s'" % (i+1,trc))
        self.twoportmode = False
    def TwoPort(self):
        windows = self.query('DISP:CAT?')
        windows = windows.strip('\n')
        print(windows == '"EMPTY"')
        if windows != '"EMPTY"':
            windows = [int(x) for x in windows.strip('"').split(',')]
            for i in windows:
                self.write('DISP:WIND%d OFF' % i)
        self.write('DISP:WIND1 ON')
        tracenames = ['CH1_S11','CH1_S21','CH1_S12','CH1_S22']
        measnames = ['S11', 'S21', 'S12', 'S22']
        for i,(meas,trc) in enumerate(zip(measnames,tracenames)):
            self.write("CALC:PAR:DEF:EXT '%s', '%s'" % (trc,meas))
            self.write("DISP:WIND:TRAC%d:FEED '%s'" % (i+1,trc))
        self.write('DISP:WIND:TRAC2:MOVE 2')
        self.write('DISP:WIND:TRAC3:MOVE 2')
        self.twoportmode = True
    def SetRange(self,start,end):
        self.SetStart(start)
        self.SetEnd(end)
    def SetCenterSpan(self,center,span):
        self.SetCenter(center)
        self.SetSpan(span)
    def SetStart(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:STAR '+mystr
        self.write(mystr)
    def SetEnd(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:STOP '+mystr
        self.write(mystr)
    def SetCenter(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:CENT '+mystr
        self.write(mystr)
    def SetSpan(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:SPAN '+mystr
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
        mystr = 'SENS:SWE:POIN '+mystr
        self.write(mystr)
    def Measure2ports(self,autoscale = True):
        if not self.twoportmode:
            self.TwoPort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND:TRAC:Y:COUP:METH WIND')
            self.write('DISP:WIND1:TRAC:Y:AUTO')
            self.write('DISP:WIND2:TRAC:Y:AUTO')
        #Read measurement (in unicode strings)  
        freq = self.query('CALC:X?')
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        tracenames = ['CH1_S11','CH1_S21','CH1_S12','CH1_S22']
        spars = [freq]
        for trc in tracenames:
            self.write("CALC:PAR:SEL '%s'" % trc)
            yy = self.query("CALC:DATA? SDATA")
            yy = np.asarray([float(xx) for xx in yy.split(',')])
            yyre = yy[::2]
            yyim = yy[1::2]
            spars.append(yyre)
            spars.append(yyim)
        #returns tuple of nparray's ordered as frequency, s11re, s11im, s21re, s21im, s12re, s12im, s22re, s22im
        return tuple(spars) 
    '''
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
    '''
    def Measure1port(self,autoscale = True):
        if self.twoportmode:
            self.SinglePort()
        print((self.query('INIT;*OPC?'))) #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND1:TRAC:Y:AUTO')
        #Read measurement (in unicode strings)  
        freq = self.query('CALC:X?')
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        tracenames = ['CH1_S11']
        spars = [freq]
        for trc in tracenames:
            self.write("CALC:PAR:SEL '%s'" % trc)
            yy = self.query("CALC:DATA? SDATA")
            yy = np.asarray([float(xx) for xx in yy.split(',')])
            yyre = yy[::2]
            yyim = yy[1::2]
            spars.append(yyre)
            spars.append(yyim)
        #returns tuple of nparray's ordered as frequency, s11re, s11im
        return tuple(spars)
# DC source commands
    '''
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
    '''