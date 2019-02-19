import numpy as np
from stlab.devices.basepna import basepna


def numtostr(mystr):
    return '%20.15e' % mystr


#    return '%20.10f' % mystr


class FieldfoxPNA(basepna):
    def __init__(self,
                 addr='TCPIP::192.168.1.151::INSTR',
                 reset=True,
                 verb=True,
                 mode='NA'):
        super(FieldfoxPNA, self).__init__(addr, reset, verb)
        if reset:
            if mode == 'NA':
                self.write('INST:SEL "NA"')  #set mode to Network Analyzer
                self.TwoPort()
            elif mode == 'SA':
                self.write('INST:SEL "SA"')  #set mode to Spectrum Analyzer

##### ABSTRACT METHODS TO BE IMPLEMENTED ON A PER PNA BASIS #####################

    def GetFrequency(self):
        frec = self.query('FREQ:DATA?')
        #Convert to numpy arrays
        frec = np.array(list(map(float, frec.split(','))))
        return frec

    def GetTraceNames(self):
        nmeas = self.query('CALC:PAR:COUN?')
        nmeas = int(nmeas)
        print(nmeas)
        pars = [
            self.query('CALC:PAR' + str(i + 1) + ':DEF?').strip('\n')
            for i in range(0, nmeas)
        ]
        print(
            pars
        )  #parameter identifiers do not exist in the fieldfox.  Indices are used.  Just return parameter names twice to keep form.
        return pars, pars

    def SetActiveTrace(self, mystr):
        pars, _ = self.GetTraceNames()
        i = pars.index(mystr)
        self.write('CALC:PAR' + str(i + 1) + ':SEL')

    def GetTraceData(self):
        yy = self.query('CALC:DATA:SDATA?')
        yy = np.asarray([float(xx) for xx in yy.split(',')])
        yyre = yy[::2]
        yyim = yy[1::2]
        return yyre, yyim

    def CalOn(self):
        mystr = "CORR:USER 1"
        self.write(mystr)

    def CalOff(self):
        mystr = "CORR:USER 0"
        self.write(mystr)

    def GetCal(self):
        return bool(int(self.query('CORR:USER?')))

### OPTIONAL METHODS

    def Measure2ports(self, autoscale=True):
        self.TwoPort()
        self.Trigger()
        if autoscale:
            self.write('DISP:WIND:TRAC1:Y:AUTO')  #Autoscale both traces
            self.write('DISP:WIND:TRAC2:Y:AUTO')  #Autoscale both traces
        return self.GetAllData()

    def Measure1port(self, autoscale=True):
        self.SinglePort()
        self.Trigger()
        if autoscale:
            self.write('DISP:WIND:TRAC1:Y:AUTO')  #Autoscale both traces
        return self.GetAllData()

    def LoadState(self, statefile):
        mystr = 'MMEM:LOAD:STAT "%s"' % statefile
        self.write(mystr)

    def SinglePort(self):
        self.write('CALC:PAR:COUN 1')  #Set 1 trace and measurement
        self.write('CALC:PAR1:DEF S11')

    def TwoPort(self):
        self.write('CALC:PAR:COUN 2')  #Set 2 traces and measurements
        self.write('CALC:PAR1:DEF S11')
        self.write('CALC:PAR2:DEF S21')

# DC source commands

    def EnableDCsource(self, reset=True):
        if reset:
            self.write('SYST:VVS:VOLT 1.00')
        self.write('SYST:VVS:ENAB 1')
        return

    def DisableDCsource(self):
        self.write('SYST:VVS:ENAB 0')
        return

    def SetDCvoltage(self, vv):
        mystr = numtostr(vv)
        mystr = 'SYST:VVS:VOLT ' + mystr
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

    def SetResBW(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:BAND:RES ' + mystr
        self.write(mystr)

    def SetVidBW(self, x):
        mystr = numtostr(x)
        mystr = 'SENS:BAND:VID ' + mystr
        self.write(mystr)

    def SetCWFreq(self, x):
        mystr = numtostr(x)
        mystr = 'ISO:FREQ ' + mystr
        self.write(mystr)

    def SetCWPower(self, x):
        mystr = numtostr(x)
        mystr = 'ISO:POW ' + mystr
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

    def MeasureSpectrum(self, autoscale=True):
        print((self.query('INIT;*OPC?')
               ))  #Trigger single sweep and wait for response
        if autoscale:
            self.write('DISP:WIND:TRAC:Y:AUTO')  #Autoscale both traces
        #Read measurement (in unicode strings)


#        frec = self.query('FREQ:DATA?')
        freqstart = float(self.query('FREQ:STAR?'))
        freqstop = float(self.query('FREQ:STOP?'))
        npoints = float(self.query('SWE:POIN?'))
        step = (freqstop - freqstart) / (npoints - 1)
        frec = np.arange(freqstart, freqstop + step, step)
        spec = self.query('TRAC:DATA?')
        #Convert to numpy arrays
        spec = np.asarray(list(map(float, spec.split(','))))
        return (frec, spec)
