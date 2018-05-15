# Basic interface to retrieve temperature measurement form BF computer

from stlab.utils.MySocket import MySocket
import time

#All writes are queries.  If command does not contain a '?', an empty string is returned.
class BFWrapper:
    def __init__(self,addr="localhost",port=8472,reset=True,verb=True,**kwargs):
        self.verb = verb
    #    if reset:
    #        self.reset()
        self.addr = addr
        self.port = port
        self.htr_ranges = (0, 0.0316, 0.1, 0.316, 1., 3.16, 10., 31.6, 100.) #For heater current ranges. 0 = Off, 1 = 31.6 μA, 2 = 100 μA, 3 = 316 μA, 4 = 1.00 mA, 5 = 3.16 mA, 6 = 10.0 mA, 7 = 31.6 mA, 8 = 100 mA
    def query(self,mystr):
        s = MySocket()
        s.sock.connect((self.addr, self.port))
        if self.verb:
            print(mystr)
        s.mysend(mystr.encode('utf_8'))
        word = s.myreceive()
        word = word.decode('utf_8')
        if self.verb:
            print(word)
        s.sock.close()
        return word
    def write(self,mystr):
        return self.query(mystr)
    #def reset(self): #I need a short pause after reset.  Otherwise the system may hang.  Not even '*OPC?' works
    #    out = self.query('*RST')
    #    time.sleep(0.1)
    def GetTemperature(self,i):
        if isinstance(i, int):
            if i> 6:
                print('GetTemperature: Invalid sensor')
                return -1.
        mystr = 'RDGK? {}'.format(i)
        ret = self.query(mystr)
        return float(ret)
    def SetAutorange(self,val=True):
        i = 1 #Turning autorange on changes the setting for all channels.  I just use channel 1
        oldsetting = self.query('RDGRNG? {}'.format(i))
        newsetting = oldsetting.split(',')
        newsetting.insert(0,str(i))
        #I simply read the range settings from channel 1 and change the autorange element
        if val:
            newsetting[-2] = '1'
        else:
            newsetting[-2] = '0'
        newsetting = ','.join(newsetting)
        self.write('RDGRNG {}'.format(newsetting))
        return
    def SetControl(self,mode = 4):  #1 = Closed PID loop, 2 = Zone Tuning, 3 = Open Loop, 4 = off
        self.write('CMODE {}'.format(mode))
        return
    def SetRamp(self,mode=True,rate=0.1): #Set ramp mode and rate (in K/min).  If true, temperature set point will ramp to desired value.  If false, no ramping will be done.
        rate = abs(rate)
        if mode:
            self.write('RAMP 1,{}'.format(rate))
        else:
            self.write('RAMP 0,{}'.format(rate))
    def SetHeaterValue(self,value):
        self.write('MOUT {}'.format(value))
        return
    def GetHeaterValue(self):
        return float(self.query('MOUT?'))
    def SetHeaterRange(self,range): #Specifies heater current range in mA. Will choose the minimum range to include the value given as "range"
        range = abs(range)
        rngi = -1
        for i,rr in enumerate(self.htr_ranges):
            if range <= rr:
                rngi = i
                break
        if rngi < 0:
            print('SetHeaterRange: Error, range too high.  No range change done.')
            return
        self.write('HTRRNG {}'.format(rngi))
        return
    def GetHeaterRange(self):
        rr = int(self.query('HTRRNG?'))
        return(self.htr_ranges[rr])
    def SetPIDTemperature(self,value=0.): #Set ramp mode and rate (in K/min).  If true, temperature set point will ramp to desired value.  If false, no ramping will be done.
        self.write('SETP {}'.format(value))
        return
    def GetSetPoint(self):
        result = self.query('SETP?')
        result = float(result)
        return result
    def WaitForTStable(self,channel=6,tol=0.001,timeout=600.,tsettle=40.):
        Tset = self.GetSetPoint()
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
                    print('T in tolerance.  Settling...')
            elif abs(TT-Tset)>=tol:
                if tstablestart != None:
                    print('T left tolerance')
                tstablestart = None
                continue
            if tnow-tstablestart > tsettle:
                success = True
                break
            time.sleep(0.2)
        if success:
            print("Channel " + str(channel) + " STABLE at " + str(Tset) + ' K')
        else:
            print("Channel " + str(channel) + " UNSTABLE for " + str(Tset) + ' K')
        return success
        
    
    
    '''
    def SetMCHeater(self,xx):
        mystr = 'SET:DEV:H1:HTR:SIG:POWR:%f' % xx
        reply = self.query(mystr)
        print(reply[reply.rfind(":"):])
        return
    def SetStillHeater(self,xx):
        mystr = 'SET:DEV:H2:HTR:SIG:POWR:%f' % xx
        reply = self.query(mystr)
        print(reply[reply.rfind(":")+1:])
        return
    def SetEnableTsensor(self,ii,state=True):
        if ii>= 10:
            print('SetEnableTsensor: Invalid sensor ',ii)
            return -1.
        if state:
            mystr = 'SET:DEV:T%d:TEMP:MEAS:ENAB:ON' % ii
        elif not state:
            mystr = 'SET:DEV:T%d:TEMP:MEAS:ENAB:OFF' % ii
        reply = self.query(mystr)
        return
    '''
