import visa
import numpy as np
from stlab.devices.instrument import instrument
import time

    

class Agilent_11713B(instrument):
    def __init__(self,addr='TCPIP::192.168.1.113::INSTR',reset=False,verb=True,**kwargs):
        super().__init__(addr,reset,verb,**kwargs)


    def startup(self):
        self.write('cmdset agilent')

    def get_function(self):
        return (self.query('FUNCtion?'))

    def value(self):
        return self.query('READ?')

    def get_var_att(self):
        x=eval(self.query('ATT:X?'))
        y=eval(self.query('ATT:Y?'))
        return x+y

    def set_var_att(self, att):
        xy=divmod(att,10)
        self.write('ATT:X ' +str(xy[1]))
        self.write('ATT:Y ' +str(xy[0]*10))
        return att

    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass


if __name__ == '__main__':
    vatt = Agilent_11713B(addr='TCPIP::192.168.1.113::INSTR',reset=False,verb=True) #Initialize device communication and reset
    print(vatt.get_var_att())
