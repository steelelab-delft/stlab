import visa
import numpy as np
import time

def numtostr(mystr):
    return '%12.8e' % mystr


class CryoCon:
    def __init__(self,addr='TCPIP::192.168.1.5::5000::SOCKET',reset=True):
        self.rs = visa.ResourceManager('@py')
        self.dev = self.rs.open_resource(addr,read_termination='\r\n')
        self.channellist=['A','B','C','D']
        for channel in self.channellist: #set all units to K
            self.write('INP ' + channel + ':UNIT K')
    def write(self,mystr):
        self.dev.query(mystr + ';*OPC?')
    def query(self,mystr):
        out = self.dev.query(mystr)
        return out
    def GetTemperature(self,channel='C'):
        mystr = 'INP? ' + channel
        curr = self.query(mystr)
        if curr == '.......':
            print 'Channel ',channel,' out of range'
            curr = -20
        elif curr == '-------':
            print 'Channel ',channel,' out of range'
            curr = -20
        else:
            curr = float(curr)
	return curr
    def GetTemperatureAll(self):
        result = []
        for chan in self.channellist:
            result.append(self.GetTemperature(chan))
        return result
    def SetSetPoint(self,setp,loop=2):
        mystr = 'LOOP ' + str(loop) + ':SETP ' + str(setp)
        self.write(mystr)
    def GetSetPoint(self,loop=2):
        mystr = 'LOOP ' + str(loop) + ':SETP?'
        setp = self.query(mystr)
	return float(setp)
    def SetSetPoint(self,setp,loop=2):
        mystr = 'LOOP ' + str(loop) + ':SETP ' + str(setp)
        self.write(mystr)
    def GetSetPoint(self,loop=2):
        mystr = 'LOOP ' + str(loop) + ':SETP?'
        setp = self.query(mystr)
        channel = self.query('LOOP '+ str(loop) +':SOUR?')
        unit = self.query('INP ' + str(channel) + ':UNIT?')
        print setp
	return float(setp.strip(unit))
    def SetPman(self,setp,loop=2):
        mystr = 'LOOP ' + str(loop) + ':PMAN ' + str(setp)
        self.write(mystr)
    def GetPman(self,loop=2):
        mystr = 'LOOP ' + str(loop) + ':PMAN?'
        setp = self.query(mystr)
	return float(setp)
    def ControlOn(self):
        self.write('CONT')
        return
    def ControlOff(self):
        self.write('STOP')
        return
    def SetLoopMode(self,loop,mode):  #OFF, PID, MAN, TABLE, RAMPP
        self.write('LOOP ' + str(loop) + ':TYPE ' + str(mode))
        return
    def WaitForTStable(self,loop=2,tol=0.05,timeout=300.,tsettle=40.):
        channel = self.query('LOOP ' + str(loop) + ':SOUR?') #Get channel on chosen loop
        channel = channel.strip('CH')
        Tset = self.GetSetPoint(loop)
        t0 = time.time()
        tnow = time.time()
        tstablestart = None
        success = False
        while tnow-t0 < timeout:
            tnow = time.time()
            TT = self.GetTemperature(channel) #Get current temperature
            if abs(TT-Tset)<tol:
                if tstablestart == None:
                    tstablestart = tnow
                    print 'T in tolerance.  Settling...'
            elif abs(TT-Tset)>=tol:
                if tstablestart != None:
                    print 'T left tolerance'
                tstablestart = None
                continue
            if tnow-tstablestart > tsettle:
                success = True
                break
            time.sleep(0.2)
        if success:
            print "Channel " + channel + " STABLE at " + str(Tset) + ' K'
        else:
            print "Channel " + channel + " UNSTABLE for " + str(Tset) + ' K'
        return success




