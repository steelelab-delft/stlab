from stlab.devices.instrument import instrument
from stlab.utils.stlabdict import stlabdict
import numpy as np

class keysight_EXA(instrument): 
    def __init__(self,addr = 'TCPIP::192.168.1.228::INSTR',reset=True,verb=True):
        super(keysight_EXA, self).__init__(addr,reset,verb)

    
    def SetStart(self,x):
        mystr = 'FREQ:STAR {}'.format(x)
        self.write(mystr)
    def SetStop(self,x):
        mystr = 'FREQ:STOP {}'.format(x)
        self.write(mystr)
    def SetCenter(self,x):
        mystr = 'FREQ:CENT {}'.format(x)
        self.write(mystr)
    def SetSpan(self,x):
        mystr = 'FREQ:SPAN {}'.format(x)
        self.write(mystr)
    def SetResolutionBW(self,x):
        mystr = 'BAND:RES {}'.format(x)
        self.write(mystr)
    def GetResolutionBW(self):
        mystr = 'BAND:RES?'
        x = self.query(mystr)
        return float(x)
    
    def MeasureScreen(self):
        result = self.query('READ:SAN?')
        result = result.split(',')
        result = [float(x) for x in result]
        result = np.asarray(result)
        xx = result[::2]
        yy = result[1::2]
        output = stlabdict()
        output['Frequency (Hz)'] = xx
        output['PSD (dBm)'] = yy
        output.addparcolumn('Res BW (Hz)', self.GetResolutionBW())
        return output
        
        
    
    '''
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
    '''

    