import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%12.8e' % mystr

    

class stanfordCS580(instrument):
    def __init__(self,addr='TCPIP::192.168.1.14::1470::SOCKET',reset=True,verb=True):
        #Needs \r\n line termination
        super(stanfordCS580, self).__init__(addr,reset,verb,read_termination='\n')
        self.id()
    def SetGain(self,ii):
    #Sets the gain of the source.  The full range is always +-2V times the gain value
    #0 -> 1 nA/V
    #1 -> 10 nA/V
    #2 -> 100 nA/V
    #3 -> 1 uA/V
    #4 -> 10 uA/V
    #5 -> 100 uA/V
    #6 -> 1 mA/V
    #7 -> 10 mA/V
    #8 -> 50 mA/V
        self.write('GAIN %d' % ii)
        return
    def SetCurrent(self,curr):
        mystr = numtostr(curr)
        self.query('CURR ' + mystr + ';*OPC?')
        return
    def GetCurrent(self):
        mystr = self.query('CURR?')
        return float(mystr)
    def GetSpeed(self): #0 is fast, 1 is slow
        mystr = self.query('RESP?')
        return int(mystr)
    def SetSpeed(self,ii):  #0 is fast, 1 is slow
        self.write('RESP %d' % ii)
        return
    def SetFloating(self): #Activates floating ground
        self.write('ISOL 1')
        return
    def SetGround(self): #Connects ground to the chassis (reverse of SetFloating)
        self.write('ISOL 0')
        return
    def GetIsolation(self): #1 is floating, 0 is ground
        mystr = self.query('ISOL?')
        return int(mystr)
    def SetOn(self):
        self.query('SOUT 1;*OPC?')
        return
    def SetOff(self):
        self.write('SOUT 0')
        return