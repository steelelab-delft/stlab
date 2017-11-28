# Basic interface to retrieve temperature measurement form Triton computer

from stlab.utils.MySocket import MySocket

class TritonWrapper:
    def __init__(self,addr="localhost",port=8472,reset=True,verb=True,**kwargs):
        self.verb = verb
        if reset:
            self.reset()
        self.addr = addr
        self.port = port
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
    def GetTurbo(self): #Returns turbo values in order Power, Speed, PST, MT, BT, PBT, ET (temperatures... whatever they mean...)
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
    def reset(self): #No reset for the triton
        pass
    def setverbose(self,verb=True):
        self.verb = verb
    def SetPID(self,val = True):
        if val:
            self.write('SET:DEV:T8:TEMP:LOOP:MODE:ON')
        else:
            self.write('SET:DEV:T8:TEMP:LOOP:MODE:OFF')
        return
    def SetHeaterRange(self,val):  #Value is in mA
        self.write('SET:DEV:T8:TEMP:LOOP:RANGE:{}'.format(val))
        return
    def SetPIDTemperature(self,val=0.):
        self.write('SET:DEV:T8:TEMP:LOOP:TSET:{}'.format(val))
        return

    def GetPTC(self): #Returns PTC values in order WIN, WOT, OILT, HT, HLP, HHP, MCUR, HRS
        result = []
 
        temps = ['WIT','WOT','OILT','HT']
        for ss in temps:
            mystr = self.query('READ:DEV:C1:PTC:SIG:{}'.format(ss))
            mystr = mystr.split(':')[-1]
            mystr = mystr.strip('C')
            result.append(float(mystr))

        mystr = self.query('READ:DEV:C1:PTC:SIG:HLP')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('B')
        result.append(float(mystr))
        
        mystr = self.query('READ:DEV:C1:PTC:SIG:HHP')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('B')
        result.append(float(mystr))

        mystr = self.query('READ:DEV:C1:PTC:SIG:MCUR')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('A')
        result.append(float(mystr))

        mystr = self.query('READ:DEV:C1:PTC:SIG:HRS')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('h')
        result.append(float(mystr))
        return result
