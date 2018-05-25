# Basic visa instrument class.  Includes resoruce manager startup, basic query and write methods, id and reset methods
import visa
from stlab.devices.base_instrument import base_instrument

#Try to use NI-VISA
#If this fails, revert to using pyvisa-py
def makeRM():
    try:
        global_rs = visa.ResourceManager('@ni')
        print('Global NI ResourceManager created')
        return global_rs,'@ni'
    except OSError:
        return makeRMpy()

def makeRMpy():
    global_rs = visa.ResourceManager('@py') #Create resource manager using NI backend
    print('Global pyvisa-py ResourceManager created')
    return global_rs,'@py'
    


class instrument(base_instrument):
    global_rs = None #Static resource manager for all instruments.  rstype is '@ni' for NI backend and '@py' for pyvisa-py
    rstype = None 
    def __init__(self,addr,reset=False,verb=True,**kwargs):
        if not self.global_rs or not self.rstype:
            self.global_rs, self.rstype = makeRM()
#        self.rs = visa.ResourceManager('@py')
#        self.dev = self.rs.open_resource(addr)

        #To correct serial resource naming depending on backend...  @py uses ASRLCOM1 and @ni uses ASRL1
        if 'ASRL' in addr:
            if self.rstype == '@py':
                if 'ASRLCOM' not in addr:
                    idx = addr.find('ASRL')+4
                    addr = addr[:idx] + 'COM' + addr[idx:]
            if self.rstype == '@ni':
                if 'ASRLCOM' in addr:
                    idx = addr.find('ASRL')+4
                    addr = addr[:idx] + addr[idx+3:]        

        #I have found that all our socket TCPIP devices need a \r\n line termination to work...  Add to kwargs it if not overridden
        read_termination = None
        if 'SOCKET' in addr:
            read_termination = '\r\n'
        if 'read_termination' not in kwargs:
            kwargs['read_termination'] = read_termination
        #Attempt to initialize instrument using current resource manager
        try:
            self.dev = self.global_rs.open_resource(addr,**kwargs)
        #If NI visa fails, attempt to use pyvisa-py
        except AttributeError:
            print('NI backend not working... Trying pyvisa-py')
            instrument.global_rs, instrument.rstype = makeRMpy()
            #To correct serial resource naming depending on backend...  @py uses ASRLCOM1 and @ni uses ASRL1
            if ('ASRL' in addr) and ('ASRLCOM' not in addr):
                idx = addr.find('ASRL')+4
                addr = addr[:idx] + 'COM' + addr[idx:]
            self.dev = self.global_rs.open_resource(addr,**kwargs)
        self.verb = verb  #Whether to print commands on screen
        if reset:
            self.reset()
        super().__init__()

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
        if self in base_instrument.instrument_list: base_instrument.instrument_list.remove(self) #Remove yourself from the instrument_list
        return

    
