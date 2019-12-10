"""Module for instance of a R&S SMB100A signal generator

This module contains the functions necessary to control and read data from 
a R&S SMB100A signal generator. It inherits from instrument class.

"""

from stlab.devices.instrument import instrument


def numtostr(mystr):
    return '%12.8e' % mystr


class RS_SMB100A(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.216::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.id()

    def SetFrequency(self, frec):
        mystr = numtostr(frec)
        mystr = 'FREQ:CW ' + mystr
        self.write(mystr)

    def GetFrequency(self):
        mystr = 'FREQ:CW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def SetPower(self, x):
        mystr = numtostr(x)
        mystr = 'SOUR:POW:POW ' + mystr
        self.write(mystr)

    def GetPower(self):
        mystr = 'SOUR:POW:POW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    def SetPowerOn(self):
        self.write('OUTP ON')

    def SetPowerOff(self):
        self.write('OUTP OFF')

    def SetReference(self, ref='INT'):
        # INT, EXT, ELO
        self.write('ROSC:SOUR ' + ref)

    def GetMetadataString(
            self
    ):  # Should return a string of metadata adequate to write to a file
        pass

        # requires external trigger
    def set_RF_sweep(self,freqcenter,freqspan,freqstep):
        #set sweeping mode

        self.write('SOUR:SWE:FREQ:MODE STEP')

        #setting centre freq
        mystr_fcent = numtostr(freqcenter)
        mystr_fcent = 'SOUR:FREQ:CENT ' + mystr_fcent + 'Hz'
        self.write(mystr_fcent)
        #setting frequency span
        mystr_span = numtostr(freqspan)
        mystr_span = 'SOUR:FREQ:SPAN ' + mystr_span + 'Hz'
        self.write(mystr_span)
        #setting frequency step
        mystr_step = numtostr(freqstep)
        mystr_step = 'SOUR:SWE:FREQ:STEP:LIN ' + mystr_step + 'Hz'
        self.write('SOUR:SWE:FREQ:SPAC')
        self.write(mystr_step)
        
        #set trigger
        self.write('TRIG:FSW:SOUR EXT')
        self.write('INP:TRIG:SLOP NEG')
        self.write('SOUR:FREQ:MODE SWE')
        self.write('SWE:RES')

