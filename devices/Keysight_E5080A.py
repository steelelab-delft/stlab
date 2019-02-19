from stlab.devices.PNAN5221A import PNAN5221A


def numtostr(mystr):
    return '%20.15e' % mystr


#    return '%20.10f' % mystr


class Keysight_E5080A(PNAN5221A):
    def __init__(self,
                 addr='TCPIP::192.168.1.105::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
