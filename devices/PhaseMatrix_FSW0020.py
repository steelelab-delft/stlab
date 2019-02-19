"""Module for instance of a FSW0020 phase matrix

This module contains the functions necessary to control and read data from 
a FSW0020 phase matrix. It inherits from instrument class.

"""

import time
from stlab.devices.instrument import instrument


class PhaseMatrix_FSW0020(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.220::10001::SOCKET',
                 reset=False,
                 verb=True):
        super().__init__(addr, reset, verb=verb, read_termination='\r\n')
        time.sleep(0.5)
        self.id()

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass

    def write(
            self, msg
    ):  #Pause after writing a command (can trip up the machine... if not paused...)
        super().write(msg)
        time.sleep(0.1)

    def SetFrequency(self, x):
        self.write('FREQ ' + str(x * 1000.)
                   )  #FSW takes frequencies in mHz.  Input should be in hertz
        return

    def GetFrequency(self):
        try:
            result = float(self.query('FREQ?'))
        except ValueError as err:
            print(err)
            return -1
        return result / 1000.  #FSW return frequency in mHz

    def SetPower(self, x):
        self.write(
            'POW ' +
            str(x))  #FSW takes frequencies in mHz.  Input should be in hertz
        return

    def GetPower(self):
        try:
            result = float(self.query('POW?'))
            return result
        except ValueError as err:
            print(err)
            return -1

    def RFon(self):
        self.write('OUTP:STAT ON')
        return

    def RFoff(self):
        self.write('OUTP:STAT OFF')
        return

    def GetRFstat(self):
        result = self.query('OUTP:STAT?')
        return result
