# Basic visa instrument class.  Includes resoruce manager startup, basic query and write methods, id and reset methods
import visa

class instrument:
    def __init__(self,addr,reset=True):
        self.rs = visa.ResourceManager('@py')
        self.dev = self.rs.open_resource(addr)
        if reset:
            self.reset()
    def write(self,mystr):
        print(mystr)
        self.dev.write(mystr)
    def query(self,mystr):
        print(mystr)
        out = self.dev.query(mystr)
        return out
    def id(self):
        out = self.query('*IDN?')
        print(out)
        return out
    def reset(self):
        out = self.write('*RST')
        return out
