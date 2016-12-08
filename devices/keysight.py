import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%12.8e' % mystr


class keysightB2901A(instrument):
    def __init__(self,addr='TCPIP::192.168.1.55::INSTR',reset=True,verb=True):
        super(keysightB2901A, self).__init__(addr,reset,verb)
        self.id()
    #OLD READ METHOD WITH OPC... NOT SURE IF NECESSARY. IF COMMENTED WILL USE INHERITED FROM instrument
    def write(self,mystr):
        writestr = mystr+';*OPC?'
        self.dev.query(writestr)
        if self.verb:
            print(writestr)
    def SetModeCurrent(self):
        self.write(':SOUR:FUNC:MODE CURR')
    def SetModeVoltage(self):
        self.write(':SOUR:FUNC:MODE VOLT')
    def SetOutputOn(self):
        self.write(':OUTP ON')
    def SetOutputOff(self):
        self.write(':OUTP OFF')
    def SetCurrent(self,curr):
        mystr = numtostr(curr)
        mystr = ':SOUR:CURR '+mystr
        self.write(mystr)
    def SetVoltage(self,curr):
        mystr = numtostr(curr)
        mystr = ':SOUR:VOLT '+mystr
        self.write(mystr)
    def SetComplianceVoltage(self,volt):
        mystr = numtostr(volt)
        mystr = ':SENS:VOLT:PROT ' + mystr
        self.write(mystr)
    def GetCurrent(self):
        mystr = ':MEAS:CURR?'
        curr = self.query(mystr)
        curr = float(curr)
        return curr
    def GetVoltage(self):
        mystr = ':MEAS:VOLT?'
        volt = self.query(mystr)
        volt = float(volt)
        return volt
    def GetVoltCurr(self):
        mystr = 'FORM:ELEM:SENS VOLT,CURR'
        self.write(mystr)
        mystr = ':MEAS?'
        outstr = self.query(mystr)
        data = np.array(list(map(float, outstr.split(','))))
        return (data[0],data[1])
