import visa
import numpy as np
from stlab.devices.instrument import instrument
from stlab.devices.PNAN5221A import PNAN5221A

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class PNAN5222A(PNAN5221A):
    def __init__(self,addr='TCPIP::192.168.1.42::INSTR',reset=True,verb=True):
        super().__init__(addr,reset,verb)
    def TwoPortSetup(self,port1=1,port2=2):
        ports = [port1,port2]
        trcnames = self.GetTrcNames()
        measnames = ['S%d%d' % (b,a) for a in ports for b in ports]
        if trcnames == measnames:
            return
        self.ClearAll()
        self.write('DISP:WIND1 ON')
        tracenames = ['CH1_S%d%d' % (b,a) for a in ports for b in ports]
        for i,(meas,trc) in enumerate(zip(measnames,tracenames)):
            self.write("CALC:PAR:DEF:EXT '%s', '%s'" % (trc,meas))
            self.write("DISP:WIND:TRAC%d:FEED '%s'" % (i+1,trc))
        self.write('DISP:WIND:TRAC2:MOVE 2')
        self.write('DISP:WIND:TRAC3:MOVE 2')