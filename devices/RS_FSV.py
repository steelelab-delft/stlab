from stlab.devices.instrument import instrument
import numpy as np

class RS_FSV(instrument): 

    def __init__(self,addr = '192.168.1.102',reset=True,verb=True):
        super(RS_FSV, self).__init__(addr,reset,verb)

    def prepare_CW(CWsource_addr):
        """
        Initializing FSV with SMB100A for a CW measurement: VNA mode;
        Note that SMB100A needs to be connected;
        Also connect the clock of of SMB100A to FSV. No TTL handshake yet;
       
        """
        self._CWsource = CWsource_adrr
        self.reset()
        self.write('INST:NSEL 1')                           # Select mode sweepmode=1
        self.write('INIT:CONT OFF')                         # Turn off continious sweep
        self.write('ROSC:SOUR EXT')                         # sync FSV with generator
        # Configure external tracking generator: SMB100A RF source
       
        self.write('SYST:COMM:RDEV:GEN1:TYPE \'SMB100A12\'') # generator type
        self.write('SYST:COMM:RDEV:GEN1:INT TCP')            # connection type
        self.write('SYST:COMM:TCP:RDEV:GEN1:ADDR ' + self._CWsource)    # IP adress of generator
        self.write('SOUR:EXT1:ROSC INT')                      # specify oscillator for generator
       
       
    def prepare_TD(self, LOsource_addr):
        """
        Prepare FSV for time domain measurement.
        Set external trigger.
        Use IQ aquisition mode
        """
        
        self._LOsource_addr = LOsource_addr
        self.reset()
        self.write('ROSC:SOUR EXT')                         # sync FSV with generator
        self.write('SYST:COMM:RDEV:GEN1:TYPE \'SMB100A12\'') # generator type
        self.write('SYST:COMM:RDEV:GEN1:INT TCP')            # connection type
        self.write('SYST:COMM:TCP:RDEV:GEN1:ADDR ' + self._LOsource_addr)    # IP adress of generator
        self.write('SOUR:EXT1:ROSC INT')                      # specify oscillator for generator
        
        #COnfiguring IQ mode
        self.write('INST:SEL IQ')                           # Select VSA mode, extraction of IQ
        self.write('TRIG:SOUR EXT')                           # Set trigger to external AWG
        self.write('TRIG: POS')                               # will trigger on positive slope to start 
                                                              # measurement
        self.write('INP:SEL RF')                                                     
        self.write('INP:GAIN:STAT ON')
        
        
        
        
        

    def frequency_sweep(self,fstart,fstop):
        self.initialize_CW('192.168.1.25')
        self.write('SOUR:EXT1 ON')
        self._fstart = self.num2str(fstart)
        self._fstop = self.num2str(fstop)
        self.write('FREQ:STAR ' + self._fstart+'Hz')
        self.write('SWE:POIN ' + self.num2str(1000))
        self.write('FREQ:STOP ' + self._fstop+'Hz')
        
        self.write('SWE:COUN 10')
        self.write('AVER:STAT ON')
        self.write('INIT;*WAI')
        
        self.write('SOUR:EXT1 OFF')
        #extract data

    
    def frequency_power_sweep(fstart,fstop,fstep,pstart,pstop,pstep):
        pass
        # Write code for powersweep
   
        
    
    def DisplayOn(self):
        self.write('SYST:DISP:UPD ON')
        
    def DisplayOff(self):
        self.write('SYST:DISP:UPD OFF')
         
    def set_CWsource(self,adrr):
        self._CWsource = adrr
     
    def set_LOsource(self,addr):
        self._LOsource = addr
        
    def set_CW_power(self,power): 
        self._CWpower = self.num2str(power)
        self.write('SOUR:EXT1:POW '+ self._CWpower)
        
    def set_LO_power(self,power):
        self._LOpower = self.num2str(power)
        self.write('SOUR:EXT1:POW '+ self._LOpower)
        
    def set_LO_frequency(self,freq):
        self._LO_frequency = self.num2str(freq)
        self.write('FREQ:CENT '+ self._LO_frequency +' Hz')
    
    def num2str(self, num):
        return '%12.8e' % num    
    

    