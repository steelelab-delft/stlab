from stlab.devices.instrument import instrument
from pydoc import locate
import os.path
import time

class DeviceNotFound(Exception):
    pass

    
def get_instr_definitions():
    filename = 'dev_ids.txt'
    filename = os.path.join(os.path.dirname(__file__), filename)
    devdict = {}
    with open(filename,'r') as ff:
        for line in ff:
            if line[0] == '#':
                continue
            line = line.strip()
            line = line.split(', ')
            devdict[line[0]] = line[1]
    return devdict
    
devdict = get_instr_definitions()

class test_instrument(instrument):  #instrument is abstract and can't be instantiated... I use this placeholder instrument
    def GetMetadataString(self):
        return self.id()

def autodetect_instrument(addr,reset = False, verb = True, **kwargs):

    dev = test_instrument(addr,reset,verb, query_delay = 100e-3, **kwargs)
    idstr = dev.id()

    dev.close()


    found = False
    for idtag in devdict:
        if (',' + idtag + ',' in idstr) or (', ' + idtag + ',' in idstr) or (',' + idtag + ' ,' in idstr):
            found = True
            devstr = devdict[idtag]
            devclass = 'stlab.devices.' + devstr + '.' + devstr
            print('Device found at address {}: {}'.format(addr,devstr))
            break
    if found is False:
        raise DeviceNotFound('Id string retrieved ("{}"), but not among known devices'.format(idstr))

    devclass = locate(devclass)
    
    dev = devclass(addr,reset,verb,**kwargs) #Instantiate with the proper instrument and device
    return dev

'''
if __name__ == "__main__":
    dev = autodetect_instrument('TCPIP::192.168.1.23::INSTR')
'''    
