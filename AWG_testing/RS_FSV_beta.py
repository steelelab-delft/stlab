# Written by: Sarwan Peiter

from stlab.AWG_testing.instrument import instrument
import numpy as np

class RS_FSV(instrument): 

    def __init__(self,addr = '192.168.1.102',reset=True,verb=True, **kw):
        super(RS_FSV, self).__init__(addr,reset,verb)
        self._srate = kw.pop('s_rate', 45)


    def set_IQ_mode(self):
        # Select IQ analyzer mode, extraction of IQ
        self.write('TRAC:IQ ON')
        # For testing we use evaluation mode  
        self.write('TRAC:IQ:EVAL ')
        self.write('CALC:FORM RIM')

    def set_clock_ext(self):
        # sync FSV with external clock of 10 MHz
        self.write('ROSC:SOUR EXT 10')                      

    def display(self, mode):
        # mode can be 'on' or 'off'
        mode = mode.upper()
        self.write('SYST:DISP:UPD ' + mode)

    def set_trigger_ext(self):
        # Set trigger on positive slope from external device
        self.write('TRIG:SOUR EXT')     
        self.write('TRIG: POS')                               

    def set_LO_frequency(self, freq):
        self._LO_frequency = self.num2str(freq)
        self.write('FREQ:CENT '+ self._LO_frequency +' Hz')

    def set_pre_amp(self, mode):
        # mode can be 'on' or 'off'
        mode = mode.upper()
        self.write('INP:GAIN:STAT '+ mode)

    def set_50_input_imp(self):
        # set the input impedance to 50 Ohm
        self.write( 'INP:IMP 50')

    def sel_rf_inp(self):
        self.write('INP:SEL RF')    

    def start(self):
        self.write('INIT;*WAI')

    def stop(self):
        pass


    def set_outp_sample_rate(self,freq):
        self._srate = self.num2str(freq) 
        self.write('TRACE:IQ:SRATE '+ self._srate + ' MHZ')

    def set_nr_traces(self,avg):
        # Do not use this!!!
        # avg = scalar [int]
        self_avg = int(avg)
        self.write('TRAC:IQ:AVER: ON')
        self.write('TRAC:IQ:AVER:COUN {}'.format(self._avg))

    def set_sweep_time(self,tsweep):
        """ Given a sweep time, the numbers of samples is given by
        the sweep time multiplied by the output sample rate;
        tsweep = scalar [s] """

        nrsamples = int(tsweep * self._srate)
        self.write('TRAC:IQ:RLEN {}'.format(nrsamples))


    def get_trace_data(self):
        """REAL data are transmitted as 32-bit IEEE 754 floating-point numbers"""
        self.write('FORM REAL,32')

        return self.query('TRAC:IQ:DATA:MEM?')



    def num2str(self, num):
        return '%12.8e' % num    
    

    # def prepare_CW(CWsource_addr):
    #     """
    #     Initializing FSV with SMB100A for a CW measurement: VNA mode;
    #     Note that SMB100A needs to be connected;
    #     Also connect the clock of of SMB100A to FSV. No TTL handshake yet;
       
    #     """
    #     self._CWsource = CWsource_adrr
    #     self.reset()
    #     self.write('INST:NSEL 1')                           # Select mode sweepmode=1
    #     self.write('INIT:CONT OFF')                         # Turn off continious sweep
    #     self.write('ROSC:SOUR EXT')                         # sync FSV with generator
    #     # Configure external tracking generator: SMB100A RF source
       
    #     self.write('SYST:COMM:RDEV:GEN1:TYPE \'SMB100A12\'') # generator type
    #     self.write('SYST:COMM:RDEV:GEN1:INT TCP')            # connection type
    #     self.write('SYST:COMM:TCP:RDEV:GEN1:ADDR ' + self._CWsource)    # IP adress of generator
    #     self.write('SOUR:EXT1:ROSC INT')                      # specify oscillator for generator
       
       
    # def prepare_TD(self, LOsource_addr):
    #     """
    #     Prepare FSV for time domain measurement.
    #     Set external trigger.
    #     Use IQ aquisition mode
    #     """
        
    #     self._LOsource_addr = LOsource_addr
    #     self.reset()
    #     self.write('ROSC:SOUR EXT')                         # sync FSV with generator
    #     self.write('SYST:COMM:RDEV:GEN1:TYPE \'SMB100A12\'') # generator type
    #     self.write('SYST:COMM:RDEV:GEN1:INT TCP')            # connection type
    #     self.write('SYST:COMM:TCP:RDEV:GEN1:ADDR ' + self._LOsource_addr)    # IP adress of generator
    #     self.write('SOUR:EXT1:ROSC INT')                      # specify oscillator for generator
        
    #     #COnfiguring IQ mode
    #     self.write('INST:SEL IQ')                           # Select VSA mode, extraction of IQ
    #     self.write('TRIG:SOUR EXT')                           # Set trigger to external AWG
     
    #     self.write('INP:SEL RF')                                                     
    #     self.write('INP:GAIN:STAT ON')
        
        
        
        
        

    # def frequency_sweep(self,fstart,fstop):
    #     self.initialize_CW('192.168.1.25')
    #     self.write('SOUR:EXT1 ON')
    #     self._fstart = self.num2str(fstart)
    #     self._fstop = self.num2str(fstop)
    #     self.write('FREQ:STAR ' + self._fstart+'Hz')
    #     self.write('SWE:POIN ' + self.num2str(1000))
    #     self.write('FREQ:STOP ' + self._fstop+'Hz')
        
    #     self.write('SWE:COUN 10')
    #     self.write('AVER:STAT ON')
    #     self.write('INIT;*WAI')
        
    #     self.write('SOUR:EXT1 OFF')
    #     #extract data    



    