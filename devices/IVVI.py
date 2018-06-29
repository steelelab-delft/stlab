import serial
import numpy as np
import time
from stlab.devices.base_instrument import base_instrument

from enum import Enum
#Enumeration class to store polarity values
class pol(Enum):
    bipolar = 'BIP'
    positive = 'POS'
    negative = 'NEG'

# IVVI DACs basic driver.  The system only reads and writes short byte arrays.
# DOES NOT INHERIT FROM THE "INSTRUMENT" CLASS
class IVVI_DAC(base_instrument):
    # Constructor for IVVI Dac class.  Address is ASRLCOM1 if on COM1 serial port
    # The Serial parameters for this device are:
    # Baud = 115200, data bits = 8, parity = ODD, stop bit = 1
    # Constructor requires ndacs (integers, either 8 or 16) and polarity settings (listlike of strings, 'POS', 'NEG' or 'BIP')
    def __init__(self,addr='COM1',ndacs=8,polarity=('BIP','BIP'),verb=True,timeout = 2,reset=False):
        #Directly using pyserial interface and skipping pyvisa
        self.serialport = serial.Serial(addr,baudrate=115200,bytesize=serial.EIGHTBITS, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE,timeout=timeout)
        if ndacs!=8 and ndacs!=16:
            print('DAC WARNING, non-standard number of dacs.  Should be 8 or 16 but %d was given' % ndacs)
        self.ndacs = ndacs
        self.verb = verb
        self.SetPolarity(polarity)
        if reset:
            self.RampAllZero(tt=20.)
        return
        self.lastmessage = ()
        super().__init__()
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
    def getreply(self):
        reply = self.serialport.read(2)
        nbytes = reply[0]
        reply = tuple(reply + self.serialport.read(nbytes-2))
        if len(reply) != reply[0]:
            self.flush()
            raise ValueError('MALFORMED DAC READ: FLUSHED SERIALPORT')
        if self.verb:
             print("DAC reply: ", reply)
        return reply
    def writemessage(self,message):
        self.lastmessage = message
        if self.verb:
            print("DAC input: ", message)
        message = bytes(message) #convert to bytes
        self.serialport.write(message) #Perform serial write
    def flush(self):
        rep = b'a'
        while rep != b'':
            rep = self.serialport.read()
    def SetVoltage(self,dac,mvoltage):
        #We get the byte values corresponding to the desired voltage.  We need to add the polarity dependant offset from polmatrix to get the correct byte values
        (DataH, DataL) = self.mvoltage_to_bytes(mvoltage+self.polmatrix[dac-1])
        #print(DataH, DataL)
        #Prepare byte value message to send
        message = (7, 0, 2, 1, dac, DataH, DataL)
        self.writemessage(message)
        try:
            reply = self.getreply() #For some reason read_raw does not work.  This command works as a workaround to read X bytes from the device
        except ValueError as error:
            print('Error when setting:' + repr(error))
        setmvoltage = (DataH*256 + DataL)/65535.*4000. - self.polmatrix[dac-1]
        print('DAC {} set to {} mV'.format(dac,setmvoltage))
    def SetValue(self,dac,val):
        val = int(val)
        #We get the byte values corresponding to the desired voltage.  We need to add the polarity dependant offset from polmatrix to get the correct byte values
        DataH = int(val/256)
        DataL = val - DataH*256
        #print(DataH, DataL)
        #Prepare byte value message to send
        message = (7, 0, 2, 1, dac, DataH, DataL)
        self.writemessage(message) #Perform raw write
        try:
            reply = self.getreply() #For some reason read_raw does not work.  This command works as a workaround to read X bytes from the device
        except ValueError as error:
            print('Error when setting:' + repr(error))
    def RampVoltage(self,dac,mvoltage,tt=5.,steps=100): #To ramp voltage over 'tt' seconds from current DAC value.
        v0 = self.ReadDAC(dac)
        if np.abs(v0-mvoltage)<1.:
            self.SetVoltage(dac,mvoltage)
            return
        voltages = np.linspace(v0,mvoltage,steps)
        twait = tt/steps
        for vv in voltages:
            self.SetVoltage(dac,vv)
            time.sleep(twait)
    def ReadDACs(self):
        #Prepare message to read bytes from DACS
        message = (4, 0, self.ndacs*2+2, 2)
        self.writemessage(message) #Write request for data
        try:
            reply = self.getreply() #For some reason read_raw does not work.  This command works as a workaround to read X bytes from the device
        except ValueError as error:
            print('Error when reading:' + repr(error))
            print('Assuming 0V DAC values. 5 sec to abort...')
            time.sleep(5)
            raise
            return tuple([0 for i in range(self.ndacs)])
        voltvals = self.numbers_to_mvoltages(reply[2:]) #convert the byte values to actual voltage values
        return voltvals
    def ReadDAC(self,dac):
        vs = self.ReadDACs()
        return vs[dac-1]
    def SetAllZero(self):
        for i in range(1,self.ndacs+1):
            self.SetVoltage(i,0.)
        return
    def RampAllZero(self,tt=5.,steps=100):
        v0s = self.ReadDACs()
        skip = True
        for x in v0s:
            if np.abs(x)>1.:
                skip=False
                break
        if skip:
            self.SetAllZero()
            return
        vls = [np.linspace(vv,0.,steps) for vv in v0s]
        vls = np.transpose(np.asarray(vls))
        twait = tt/steps
        for line in vls:
            for nn,vv in enumerate(line):
                self.SetVoltage(nn+1,vv)
            time.sleep(twait)
    def close(self):
        self.serialport.close()
        return
    def GetMetadataString(self):
        return self.ReadDACs()
