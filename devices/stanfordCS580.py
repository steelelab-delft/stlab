import visa
import numpy as np
from stlab.devices.instrument import instrument
import time

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
    def GetOn(self):
        msg = self.query('SOUT?')
        #print(msg)
        msg = bool(msg)
        return msg
    def RampCurrent(self,I1,rate,nsteps = 100): #Ramp current to final value at a certain rate (in amps/sec).  nsteps is the number of current points used.
        if not self.GetOn():
            self.SetCurrent(0.)
            self.SetOn()
        I0 = self.GetCurrent()
        if I0 == I1:
            print('Warning: RampCurrent: Target equal to current value.  Nothing to do')
            return
        if np.abs(I1-I0) < rate: #if total sweep time is less than 1 second, just set
            self.SetCurrent(I1)
            return
        Istep = (I1-I0)/nsteps
        ttotal = np.abs(I1-I0)/rate #Total time in seconds
        tstep = ttotal/nsteps
        Is = np.linspace(I0,I1,nsteps)
        for I in Is:
            self.SetCurrent(I)
            time.sleep(tstep)
        return