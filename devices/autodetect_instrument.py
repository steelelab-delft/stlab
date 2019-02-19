"""Module that handles autodetection of instruments

"""

from stlab.devices.instrument import instrument
from pydoc import locate
import os.path


class DeviceNotFound(Exception):
    pass


def get_instr_definitions():
    filename = 'dev_ids.txt'
    filename = os.path.join(os.path.dirname(__file__), filename)
    devdict = {}
    with open(filename, 'r') as ff:
        for line in ff:
            if line[0] == '#':
                continue
            line = line.strip()
            line = line.split(', ')
            devdict[line[0]] = line[1]
    return devdict


devdict = get_instr_definitions()


class test_instrument(
        instrument
):  #instrument is abstract and can't be instantiated... I use this placeholder instrument
    def GetMetadataString(self):
        return self.id()


def autodetect_instrument(addr, reset=False, verb=True, **kwargs):
    """Autodetect instrument function

    Attempts automatically detect the desired instrument at the given address and creates
    a new session with it using its corresponding driver.  It uses the response from :code:`*IDN?`
    to identify the correct driver to load from the :code:`dev_ids.txt` file.  This file contains
    model string and driver name pairs that this function searches in to find the correct driver.

    Parameters
    ----------
    addr : str
        Visa address string to autodetect
    reset : bool, optional
        If True sends :code:`*RST` to the instrument after connecting to it
    verb : bool, optional
        If True, prints debugging messages and strings sent
    kwargs
        Additional parameters to be passed to the visa.open_instrument method (a common one is :code:`read_termination` for example)

    """

    dev = test_instrument(addr, reset, verb, query_delay=100e-3, **kwargs)
    idstr = dev.id()

    dev.close()

    found = False
    for idtag in devdict:
        if (',' + idtag + ',' in idstr) or (', ' + idtag + ',' in idstr) or (
                ',' + idtag + ' ,' in idstr):
            found = True
            devstr = devdict[idtag]
            devclass = 'stlab.devices.' + devstr + '.' + devstr
            print('Device found at address {}: {}'.format(addr, devstr))
            break
    if found is False:
        raise DeviceNotFound(
            'Id string retrieved ("{}"), but not among known devices'.format(
                idstr))

    devclass = locate(devclass)

    dev = devclass(
        addr, reset, verb,
        **kwargs)  #Instantiate with the proper instrument and device
    return dev


if __name__ == "__main__":
    addr = input('Enter VISA string:\n')
    dev = autodetect_instrument('TCPIP::192.168.1.23::INSTR')
    dev.id()
    print('suCCess!')
