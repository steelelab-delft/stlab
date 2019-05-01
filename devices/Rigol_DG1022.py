"""Module for instance of a Rigol DG1022 AWG

This module contains the functions necessary to control and read data from 
a Rigol DG1022 AWG. It inherits from instrument class.

"""

from stlab.devices.instrument import instrument
import time


class Rigol_DG1022(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.216::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb, query_delay=100e-3)
        self.SetRemote()
        print('\n########################################################')
        print('Caution: Sometimes the device does not respond immediately!')
        print('Be sure to either check that the setting is set correctly, or implement a while True loop and regularly check the set value!')
        # time.sleep(5)
        # self.id()

    # def query(self, mystr):
    #     self.write(mystr)
    #     time.sleep(10e-3)  # Needed so it wont crash...
    #     out = self.dev.read()
    #     return out

    def SetLocal(self):
        self.SetDisplay('ON')
        self.write('SYST:LOC')

    def SetRemote(self):
        self.SetDisplay('ON')
        self.write('SYST:REM')

    def SetShape(self, shape,ch=1):
        # {SINusoid|SQUare|RAMP|PULSe|NOISe|DC|USER}
        if ch == 1:
            self.write('FUNC {}'.format(shape))
        else:
            self.write('FUNC:CH{} {}'.format(ch, shape))
        time.sleep(1)
        return

    def GetShape(self, ch=1):
        if ch == 1:
            return self.query('FUNC?')
        else:
            return self.query('FUNC:CH{}?'.format(ch))

    def SetVpp(self, vv, ch=1):
        if ch == 1:
            self.write('VOLT:UNIT VPP')  # {VPP|VRMS|DBM}
            self.write('VOLT {}'.format(vv))
        else:
            self.write('VOLT:CH{}:UNIT VPP'.format(ch))  # {VPP|VRMS|DBM}
            self.write('VOLT:CH{} {}'.format(ch, vv))

    def GetVpp(self, ch=1):
        if ch == 1:
            self.write('VOLT:UNIT VPP')  # {VPP|VRMS|DBM}
            # time.sleep(0.1)
            result = self.query('VOLT?')
        else:
            self.write('VOLT:CH{}:UNIT VPP'.format(ch))  # {VPP|VRMS|DBM}
            # time.sleep(0.1)
            result = self.query('VOLT:CH{}?'.format(ch))
        return float(result)

    def SetVoffset(self, vv, ch=1):
        if ch == 1:
            self.write('VOLT:OFFSET {}'.format(vv))
        else:
            self.write('VOLT:CH{}:OFFSET {}'.format(ch, vv))
        return

    def SetFrequency(self, ff, ch=1):
        if ch == 1:
            self.write('FREQ {}'.format(ff))
        else:
            self.write('FREQ:CH{} {}'.format(ch, ff))

    def GetFrequency(self, ch=1):
        if ch == 1:
            result = self.query('FREQ?')
        else:
            result = self.query('FREQ:CH{}?'.format(ch))
        return float(result)

    def SetOn(self, ch=1):
        if ch == 1:
            self.write('OUTP ON')
        else:
            self.write('OUTP:CH{} ON'.format(ch))

    def SetOff(self, ch=1):
        if ch == 1:
            self.write('OUTP OFF')
        else:
            self.write('OUTP:CH{} OFF'.format(ch))

    def SetDisplay(self,state='ON'):
        self.write('DISP '+state)

    # def SetReference(self, ref='INT'):
    #     # INT, EXT
    # Note: SetReference disables the Rigol for some reason.
    # TODO: find out why
    #     self.write('SYST:CLKSRC ' + ref)

    def GetMetadataString(self):
        # Should return a string of metadata adequate to write to a file
        pass
