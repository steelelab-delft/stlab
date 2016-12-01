import visa
import numpy as np
from stlab.devices.instrument import instrument

def numtostr(mystr):
    return '%12.8e' % mystr


class RigolDM3058(instrument):
    def __init__(self,addr='TCPIP::192.168.1.216::INSTR',reset=True,verb=True):
        super(RigolDM3058, self).__init__(addr,reset,verb,write_termination='\n',read_termination='\n')
        self.id()
    def write(self,mystr):
        mystr = ':' + mystr
        if self.verb:
            print(mystr)
        self.dev.write(mystr)
    def query(self,mystr):
        mystr = ':' + mystr
        if self.verb:
            print(mystr)
        out = self.dev.query(mystr)
        return out
    def GetVoltage(self):
        mystr = 'MEAS:VOLT:DC?'
        volt = self.query(mystr)
        volt = volt.split(" ")
        volt = float(volt[-1])
        return volt
    def SetRange(self,i):  #0: 200 mV, 1: 2 V, 2: 20 V, 3: 200 V, 4: 1000 V
        mystr = "MEAS:VOLT:DC %d" % i
        self.write(mystr)
'''
        def GetVoltCurr(self):
        mystr = 'FORM:ELEM:SENS VOLT,CURR'
        self.write(mystr)
        mystr = ':MEAS?'
        outstr = self.query(mystr)
        data = np.array(list(map(float, outstr.split(','))))
        return (data[0],data[1])
'''