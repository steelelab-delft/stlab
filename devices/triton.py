#Triton communication driver.  If TritonDaemon is used (for remote logging) you should use TritonWrapper.
#Only the "query" method and _init_ is really used from this driver under those circumstances

import visa
import numpy as np
import time
from stlab.devices.instrument import instrument

class Triton(instrument):
    def __init__(self,addr='TCPIP::192.168.1.178::33576::SOCKET',reset=True,verb=True):
        #The Triton does not understand *RST so we don't reset.  Also '\n' read termination is necessary
        super(Triton, self).__init__(addr,reset=False,verb=verb,read_termination='\n')
        if reset:
            pass
    def write(self,mystr): #All writes on triton are queries
        self.query(mystr)
    def getpressure(self,i):
        mystr = 'READ:DEV:P%d:PRES:SIG:PRES' % i
        ret = self.query(mystr)
        ret = ret.split(':')
        ret = ret[-1]
        if ret == 'NOT_FOUND':
            print('Sensor P%d not found' % i)
            return -1.
        ret = ret.strip('mB')
        return float(ret)
    def gettemperature(self,i):
        if i>= 10:
            print('gettemperature: Invalid sensor')
            return -1.
        mystr = 'READ:DEV:T%d:TEMP:SIG:TEMP' % i
        ret = self.query(mystr)
        ret = ret.split(':')
        ret = ret[-1]
        if ret == 'NOT_FOUND':
            print('Sensor P%d not found' % i)
            return -1.
        ret = ret.strip('K')
        return float(ret)
    def GetTurbo(self): #Returns turbo values in order Power, Speed, PST, MT, BT, PBT, ET (temperatures)
        result = []
        
        mystr = self.query('READ:DEV:TURB1:PUMP:SIG:POWR')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('W')
        result.append(float(mystr))
        
        mystr = self.query('READ:DEV:TURB1:PUMP:SIG:SPD')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('Hz')
        result.append(float(mystr))
        
        temps = ['PST','MT','BT','PBT','ET']
        for ss in temps:
            mystr = self.query('READ:DEV:TURB1:PUMP:SIG:{}'.format(ss))
            mystr = mystr.split(':')[-1]
            mystr = mystr.strip('C')
            result.append(float(mystr))
        return result