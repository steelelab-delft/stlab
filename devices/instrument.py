# Basic visa instrument class.  Includes resoruce manager startup, basic query and write methods, id and reset methods
import visa

#Try to use pyvisa-py
#If this fails, revert to using NI-VISA
try:
    global_rs = visa.ResourceManager('@py')
    print('Global pyvisa-py ResourceManager created')
except:
    global_rs = visa.ResourceManager() #Create resource manager using NI backend
    print('Global NI ResourceManager created')


class instrument:
    def __init__(self,addr,reset=True,verb=True,**kwargs):
#        self.rs = visa.ResourceManager('@py')
#        self.dev = self.rs.open_resource(addr)
        self.dev = global_rs.open_resource(addr,**kwargs)
        self.verb = verb
        #if 'read_termination' in kwargs:
        #    self.dev.read_termination = kwargs['read_termination']
        #if 'write_termination' in kwargs:
        #    self.dev.write_termination = kwargs['write_termination']
        if reset:
            self.reset()
    def write(self,mystr):
        if self.verb:
            print(mystr)
        self.dev.write(mystr)
    def query(self,mystr):
        if self.verb:
            print(mystr)
        out = self.dev.query(mystr)
        return out
    def read(self):
        out = self.dev.read()
        return out
    def id(self):
        out = self.query('*IDN?')
        print(out)
        return out
    def reset(self):
        out = self.write('*RST')
        return out
    def setverbose(self,verb=True):
        self.verb = verb
    def close(self):
        self.dev.close()
        return
