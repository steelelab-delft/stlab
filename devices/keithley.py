import visa
import numpy as np
from stlab.devices.instrument_ni import instrument_ni

def numtostr(mystr):
    return '%12.8e' % mystr

# Driver for Keithley2100 multimeter.  Uses instrument_ni (NI backend) instead of normal instrument class
    
class Keithley2100(instrument_ni):
    def __init__(self,addr='USB0::0x05E6::0x2100::1310646::INSTR',reset=True,verb=True):
        super(Keithley2100, self).__init__(addr,reset,verb)
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
        mystr = "SENS:VOLT:DC:RANGE:AUTO %d" % int(set)
        self.write(mystr)
    def SetRange(self,range):
        self.SetRangeAuto(False)
        self.write('SENS:VOLT:DC:RANGE %s' % str(range))