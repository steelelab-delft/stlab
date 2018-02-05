from stlab.devices.instrument import instrument
from pydoc import locate

class DeviceNotFound(Exception):
    pass

devdict = {'5221A':'PNAN5221A',
    '5222A':'PNAN5222A',
    'ZND':'ZND'
    }



def autodetect_instrument(addr,reset = False, verb = True, **kwargs):

    dev = instrument(addr,reset,verb, **kwargs)
    idstr = dev.id()
    dev.close()


    found = False
    for idtag in devdict:
        if idtag in idstr:
            found = True
            devstr = devdict[idtag]
            devclass = 'stlab.devices.' + devstr + '.' + devstr
            print('Device found at address {}: {}'.format(addr,devstr))
            break
    if found is False:
        raise DeviceNotFound('Id string retrieved ("{}"), but not among known devices'.format(idstr))

    devclass = locate(devclass)
    dev = devclass(addr,reset,verb,**kwargs)
    return dev

'''
if __name__ == "__main__":
    dev = autodetect_instrument('TCPIP::192.168.1.23::INSTR')
'''    
