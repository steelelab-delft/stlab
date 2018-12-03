import numpy as np
from stlab.devices.basepna import basepna


def numtostr(mystr):
    return '%20.15e' % mystr


#    return '%20.10f' % mystr


class PNAN5221A(basepna):
    def __init__(self,
                 addr='TCPIP::192.168.1.105::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)

### OBLIGATORY METHODS TO BE IMPLEMENTED FROM ABCLASS

    def GetFrequency(self, ch=1):
        freq = self.query('CALC{}:X?'.format(ch))
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        return freq

    def GetTraceNames(self):
        pars = self.query('CALC:PAR:CAT:EXT?')
        pars = pars.strip('\n').strip('"').split(',')
        parnames = pars[1::2]
        pars = pars[::2]
        return pars,parnames

    def SetActiveTrace(self, mystr, ch=1):
        self.write('CALC{}:PAR:SEL "{}"'.format(ch, mystr))

    def GetTraceData(self, ch=1):
        yy = self.query("CALC{}:DATA? SDATA".format(ch))
        yy = np.asarray([float(xx) for xx in yy.split(',')])
        yyre = yy[::2]
        yyim = yy[1::2]
        return yyre, yyim

    #probably need checking?
    def CalOn(self):
        mystr = "SENS:CORR ON"
        self.write(mystr)
        return

    def CalOff(self):
        mystr = "SENS:CORR OFF"
        self.write(mystr)
        return

    def GetCal(self):
        return bool(int(self.query('SENS:CORR?')))

### OPTIONAL METHODS

    def SetElectricalDelay(self, t):
        '''
        Electrical delay set in seconds
        '''
        self.write("CALC:CORR:EDEL:TIME %fNS" % (t * 1e9))

    def TwoPortSetup(self):
        self.SetContinuous(False)
        trcnames = self.GetTraceNames()
        measnames = ['S11', 'S21', 'S12', 'S22']
        if trcnames == measnames:
            return
        self.ClearAll()
        self.write('DISP:WIND1 ON')
        tracenames = ['CH1_S11', 'CH1_S21', 'CH1_S12', 'CH1_S22']
        for i, (meas, trc) in enumerate(zip(measnames, tracenames)):
            self.write("CALC:PAR:DEF:EXT '%s', '%s'" % (trc, meas))
            self.write("DISP:WIND:TRAC%d:FEED '%s'" % (i + 1, trc))
        self.write('DISP:WIND:TRAC2:MOVE 2')
        self.write('DISP:WIND:TRAC3:MOVE 2')

    def Measure2ports(self, autoscale=True):
        self.TwoPortSetup()
        print((self.query('INIT;*OPC?')
               ))  #Trigger single sweep and wait for response
        if autoscale:
            self.AutoScaleAll()
        return self.GetAllData()

    def Measure1port(self, autoscale=True):
        self.SinglePortSetup()
        print((self.query('INIT;*OPC?')
               ))  #Trigger single sweep and wait for response
        if autoscale:
            self.AutoScaleAll()
        return self.GetAllData()

    def ClearAll(self):  #Clears all traces and windows
        windows = self.query('DISP:CAT?')
        windows = windows.strip('\n')
        if windows != '"EMPTY"':
            windows = [int(x) for x in windows.strip('"').split(',')]
            for i in windows:
                self.write('DISP:WIND%d OFF' % i)

    def AutoScaleAll(self):
        windows = self.query('DISP:CAT?')
        windows = windows.strip('\n')
        if windows != '"EMPTY"':
            windows = [int(x) for x in windows.strip('"').split(',')]
            for i in windows:
                tnums = self.query('DISP:WIND{}:CAT?'.format(i))
                if tnums != '"EMPTY"':
                    tnums = tnums.strip().strip('"').split(',')
                    self.write('DISP:WIND{}:TRAC{}:Y:COUP:METH WIND'.format(i,tnums[0]))
                    #self.write('DISP:WIND{}:TRAC{}:Y:AUTO'.format(i,tnums[0]))
                    self.write('DISP:WIND{}:Y:AUTO'.format(i))
                    

    def AddTraces(
            self, trcs
    ):  #Function to add traces to measurement window.  trcs is a list of S parameters Sij.
        self.write('DISP:WIND1 ON')
        if type(trcs) is str:
            measnames = [trcs]
        else:
            measnames = trcs
        tracenames = ['CH1_%s' % x for x in measnames]
        for i, (meas, trc) in enumerate(zip(measnames, tracenames)):
            self.write("CALC:PAR:DEF:EXT '%s', '%s'" % (trc, meas))
            self.write("DISP:WIND:TRAC%d:FEED '%s'" % (i + 1, trc))

    def LoadCal(self, calset):
        mystr = 'SENS:CORR:INT ON'
        self.write(mystr)
        mystr = 'SENS:CORR:CSET:ACT "%s",0' % calset
        self.write(mystr)


# For Segment sweeps
    def DelAllSegm(self):
        self.write('SENS:SEGM:DEL:ALL')
        return

    def AddSegm(self,snum=1):
        self.write('SENS:SEGM{}:ADD'.format(snum))
        return
        
    def SetSweepType(self, mystr):  #Possible values: LINear | LOGarithmic | POWer | CW | SEGMent | PHASe  (Default value is LINear)
        self.write('SENS:SWE:TYPE %s' % mystr)

    def SetCWfrequency(self, xx):
        self.write('SENS:FREQ {}'.format(xx))
        return

    def GetCWfrequency(self):
        result = float(self.query('SENS:FREQ?'))
        return result

    def SetArbitrarySegSweep(self, on=True):
        if on:
            self.write('SENS:SEGM:ARB ON')
        else:
            self.write('SENS:SEGM:ARB OFF')

    def SetSegmStart(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM:FREQ:STAR ' + mystr
        self.write(mystr)

    def SetSegmEnd(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM:FREQ:STOP ' + mystr
        self.write(mystr)
    
    def SetSegmPoints(self, x, snum=1):
        mystr = '%d' % x
        mystr = 'SENS:SEGM{}:SWE:POIN {}'.format(snum,mystr)
        self.write(mystr)
        
    def SetSegmRange(self, start, end):
        self.SetSegmStart(start)
        self.SetSegmEnd(end)

    def SetSegmState(self, state='ON'): #'ON' or 'OFF'
        self.write('SENS:SEGM {}'.format(state))
        return

    def GetSweepTime(self):
        result = self.query('SENSe:SWEep:TIME?')
        return float(result)

    #Not currently working for segments
    '''
    def SetSegmIFBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM:BWID '+mystr
        self.write(mystr)
    def SetSegmPower(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM:POW '+mystr
        self.write(mystr)
    '''

    def SetSegmPoints(self, x):
        mystr = '%d' % x
        mystr = 'SENS:SEGM:SWE:POIN ' + mystr
        self.write(mystr)

    def SetSegmRange(self, start, end):
        self.SetSegmStart(start)
        self.SetSegmEnd(end)

    def SetMeasurementFormat(self, measurement_format):
        '''
        Sets the measurement format of the main measurement
        Options are: MLIN, MLOG, PHAS, UPH, IMAG, REAL, POL, SMIT, SADM, SWR, GDEL, KELV, FAHR, CELS
        '''

        #sets the format
        self.write("CALC1:FORM " + measurement_format)
