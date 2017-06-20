# Basic interface to retrieve temperature measurement form BF computer

from stlab.utils.MySocket import MySocket

class BFWrapper:
    def __init__(self,addr="localhost",port=8472,reset=True,verb=True,**kwargs):
        self.verb = verb
    #    if reset:
    #        self.reset()
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
    #def reset(self): #I need a short pause after reset.  Otherwise the system may hang.  Not even '*OPC?' works
    #    out = self.query('*RST')
    #    time.sleep(0.1)
    def GetTemperature(self,i):
        if i> 6:
            print('GetTemperature: Invalid sensor')
            return -1.
        mystr = 'RDGK? {}'.format(i)
        ret = self.query(mystr)
        return float(ret)
    
    
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