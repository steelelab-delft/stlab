import stlab.devices.instrument as instrument
import pyvisa.constants as cts

from enum import Enum
#Enumeration class to store polarity values
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
    # Constructor requires ndacs (integers, either 8 or 16) and polarity settings (listlike of strings, 'POS', 'NEG' or 'BIP')
    def __init__(self,addr='ASRLCOM1',ndacs=8,polarity=('BIP','BIP'),verb=True,reset=True):
        # Open serial resource or other type
        if "ASRL" in addr:         
            self.dev = instrument.global_rs.open_resource(addr,baud_rate=115200,data_bits=8,parity=cts.Parity.odd,stop_bits=cts.StopBits.one)
        else:
            self.dev = instrument.global_rs.open_resource(addr)
        #Set read and write terminations.  Probably unnecessary since I am using raw reads and writes
        self.dev.read_termination=None
        self.dev.write_termination=None
        if ndacs!=8 and ndacs!=16:
            print('DAC WARNING, non-standard number of dacs.  Should be 8 or 16 but %d was given' % ndacs)
        self.ndacs = ndacs
        self.verb = verb
        self.SetPolarity(polarity)
        return

    #Function to set polarity.  This just informs the driver what polarities are in use so it can correctly set the voltages.
    #The driver cannot physically set the polarity.  The real polarity of the DACs can only be set form the hardware switches.
    def SetPolarity(self,polarity):
        if self.ndacs/4 != len(polarity):
            print('DAC WARNING: wrong number of polarity settings')
        self.polarity = [pol(x) for x in polarity]
        self.make_polmatrix()
        if self.verb:        
            print('Polarity settings')
            for x,y in zip(self.polarity,range(4)):
                print('DACs '+'%d-%d: ' % ((y+1)*4-3,(y+1)*4) + x.value)
            print('polmatrix = ', self.polmatrix)
        return
    #Makes the polmatrix varable that stores the offset voltage for each DAC channel.
    #This offset needs to be added to each channel to get the correct 0-4V value corresponding to the polarity defined range.
    def make_polmatrix(self):
        polmatrix = []
        if self.verb:
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
        the corresponding mvoltages.  Polarity offset is included.
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
        #We get the byte values corresponding to the desired voltage.  We need to add the polarity dependant offset from polmatrix to get the correct byte values
        (DataH, DataL) = self.mvoltage_to_bytes(mvoltage+self.polmatrix[dac-1])
        #print(DataH, DataL)
        #Prepare byte value message to send
        message = (7, 0, 2, 1, dac, DataH, DataL)
        if self.verb:
            print("DAC input: ", message)
        message = bytearray(message) #convert to byte array
        self.dev.write_raw(message) #Perform raw write
        reply,status = self.dev.visalib.read(self.dev.session,2) #For some reason read_raw does not work.  This command works as a workaround to read X bytes from the device
        if self.verb:
            print("DAC reply: ", tuple([x for x in reply]))
    def ReadDACs(self):
        #Prepare message to read bytes from DACS
        message = (4, 0, self.ndacs*2+2, 2)
        if self.verb:
            print("DAC input: ", message)
        message = bytearray(message)
        self.dev.write_raw(message) #Write request for data
        reply,status = self.dev.visalib.read(self.dev.session,2) #Read reply length and error byte
        if self.verb:
            print('DAC reply: ', tuple([x for x in reply]))
        nbytes = reply[0]
        reply,status = self.dev.visalib.read(self.dev.session,nbytes-2) #Read remaining reply bytes
        reply = tuple([x for x in reply])
        if self.verb:
            print('DAC reply: ', reply)
        reply = self.numbers_to_mvoltages(reply) #convert the byte values to actual voltage values
        return reply
