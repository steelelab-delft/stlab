import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%12.8e' % mystr

# Driver for Keithley2100 multimeter.  Uses instrument_ni (NI backend) instead of normal instrument class
    
class Keithley_2100(instrument):
    def __init__(self,addr='USB0::0x05E6::0x2100::1310646::INSTR',reset=True,verb=True,**kwargs):
        super().__init__(addr,reset,verb,**kwargs)
        self.id()
    def GetVoltage(self,range='DEF',res='DEF'): # (manual entry) Preset and make a DC voltage measurement with the specified range and resolution. The reading is sent to the output buffer.
        # range and res can be numbers or MAX, MIN, DEF
        # Lower resolution means more digits of precision (and slower measurement).  The number given is the voltage precision desired.  If value is too low, the query will timeout
        mystr = 'MEAS:VOLT:DC? %s,%s' % (range,res)
        volt = self.query(mystr)
        return float(volt)
    def GetCurrent(self,range='DEF',res='DEF'): # (manual entry) Preset and make a DC current measurement with the specified range and resolution. The reading is sent to the output buffer.
        # range and res can be numbers or MAX, MIN, DEF
        # Lower resolution means more digits of precision (and slower measurement).  The number given is the voltage precision desired.  If value is too low, the query will timeout
        mystr = 'MEAS:CURR:DC? %s,%s' % (range,res)
        num = self.query(mystr)
        return float(num)
# If using GetVoltage(), the following settings are ignored
    def SetRangeAuto(self,set=True):
        mystr = "SENS:" + self.GetFunction() + ":RANGE:AUTO %d" % int(set)
        self.write(mystr)
    def SetRange(self,range):
        self.SetRangeAuto(False)
        func = self.GetFunction()
        if isinstance(range, str):
            mystr = 'SENS:' + func + ':RANGE %s' % range
        else:
            mystr = 'SENS:' + func + ':RANGE %f' % range
        self.write(mystr)
        return
    def SetDisplay(self,state=True):
        if state:
            self.write('DISP ON')
        else:
            self.write('DISP OFF')
        return
    def SetFunction(self,mystr):
        self.write('FUNC ' + mystr)
        return
    def GetFunction(self):
        mystr = self.query('FUNC?')
        mystr = mystr.strip("'").strip('"').strip("'")
        if mystr == 'VOLT':
            mystr = 'VOLT:DC'
        return mystr
    def Trigger(self):
        self.write('INIT')
    def SetContinuous(self,state=True):
        if state:
            self.write('TRIG:COUN INF')
        else:
            self.write('TRIG:COUN 1')
        return
    def ReadValue(self):
        #self.SetContinuous(False)
        return self.query('READ?')
    def GetVoltageFast(self):
        x = self.GetMeasurement()
        return x
    def GetMeasurement(self):
        self.Trigger()
        x = float(self.ReadValue())
        return x
        