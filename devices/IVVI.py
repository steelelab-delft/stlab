import stlab.devices.instrument as instrument
import pyvisa.constants as cts

from enum import Enum
class pol(Enum):
    bipolar = 'BIP'
    positive = 'POS'
    negative = 'NEG'
  
# IVVI DACs basic driver.  The system only reads and writes short byte arrays.
# DOES NOT INHERIT FROM THE "INSTRUMENT" CLASS
class IVVI_DAC:
    # Constructor for IVVI Dac class.  Address is ASRLCOM1 if on COM1 serial port
    # The Serial parameters for this device are:
    # Baud = 115200, data bits = 8, parity = ODD, stop bit = 1
    def __init__(self,addr='ASRLCOM1',ndacs=8,polarity=('BIP','BIP'),verb=True,reset=True):
        # Open serial resource or other
        if "ASRL" in addr:         
            self.dev = instrument.global_rs.open_resource(addr,baud_rate=115200,data_bits=8,parity=cts.Parity.odd,stop_bits=cts.StopBits.one)
        else:
            self.dev = instrument.global_rs.open_resource(addr)
        self.dev.read_termination=None
        self.dev.write_termination=None
        self.ndacs = ndacs
        self.verb = verb
        self.SetPolarity(polarity)
        return
    def SetPolarity(self,polarity):
        self.polarity = [pol(x) for x in polarity]
        self.make_polmatrix()
        if self.verb:        
            print('Polarity settings')
            for x,y in zip(self.polarity,range(4)):
                print('DACs'+'%d-%d: ' % ((y+1)*4-3,(y+1)*4) + x.value)
            print('polmatrix = ', self.polmatrix)
        return
    def make_polmatrix(self):
        polmatrix = []
        print(self.polarity)
        for mypol in self.polarity:
            if mypol is pol.bipolar:
                polmatrix = polmatrix + [2000. for x in range(4)]
            elif mypol is pol.positive:
                polmatrix = polmatrix + [0. for x in range(4)]
            elif mypol is pol.negative:
                polmatrix = polmatrix + [4000. for x in range(4)]
        self.polmatrix = tuple(polmatrix)
        return
    def numbers_to_mvoltages(self, numbers):
        '''
        Converts a list of bytes to a list containing
        the corresponding mvoltages
        '''
        values = [ (x*256 + y)/65535.*4000. - x0 for x,y,x0 in zip(numbers[::2],numbers[1::2],self.polmatrix)]
        return tuple(values)
    def mvoltage_to_bytes(self,mvoltage):
        '''
        Converts a mvoltage on a 0mV-4000mV scale to a 16-bit integer equivalent
        output is a list of two bytes
        Input:
            mvoltage (float) : a mvoltage in the 0mV-4000mV range
    
        Output:
            (dataH, dataL) (int, int) : The high and low value byte equivalent
        '''
        bytevalue = int(round(mvoltage/4000.0*65535))
        if bytevalue > 65535 or bytevalue < 0:
            print("DAC Warning: mvoltage value out of range: ", mvoltage, bytevalue)
            print("Setting to limit")
            if bytevalue < 0:
                bytevalue = 0
            if bytevalue > 65535:
                bytevalue = 65535
        dataH = int(bytevalue/256)
        dataL = bytevalue - dataH*256
        return (dataH, dataL)
    def SetVoltage(self,dac,mvoltage):
        (DataH, DataL) = self.mvoltage_to_bytes(mvoltage+self.polmatrix[dac-1])
        #print(DataH, DataL)
        message = (7, 0, 2, 1, dac, DataH, DataL)
        if self.verb:
            print("DAC input: ", message)
        message = bytearray(message)
        self.dev.write_raw(message)
        reply,status = self.dev.visalib.read(self.dev.session,2)
        if verb:
            for x in reply:
                print("DAC reply: ", reply)
    def ReadDACs(self):
        message = (4, 0, self.ndacs*2+2, 2)
        if self.verb:
            print("DAC input: ", message)
        message = bytearray(message)
        self.dev.write_raw(message)
        reply,status = self.dev.visalib.read(self.dev.session,2)
        if self.verb:
            print('DAC reply: ', reply)
        nbytes = reply[0]
        reply,status = self.dev.visalib.read(self.dev.session,nbytes-2)
        reply = tuple([x for x in reply])
        if self.verb:
            print('DAC reply: ', reply)
        reply = self.numbers_to_mvoltages(reply)
        return reply
