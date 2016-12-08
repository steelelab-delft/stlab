# Basic interface to retrieve temperature measurement form BF computer
# Server must be running on BF computer (The server just checks temperature log and returns last logged value)
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
    def reset(self):
        pass
    def setverbose(self,verb=True):
        self.verb = verb