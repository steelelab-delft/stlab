import numpy as np
from stlab.devices.instrument import instrument
import math
import time

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class Rigol_DS1054(instrument):
    def __init__(self,addr='TCPIP::192.168.1.236::INSTR',reset=False,verb=True):
        kwargs = {}
        kwargs['timeout'] = 10000
        super().__init__(addr,reset,verb,**kwargs)
        #self.write('STOP')


    def AutoScale(self):
        # autoscale
        self.write(':AUT')
        self.query('*OPC?')
        return

    def SetVoltScale(self,scal,n=1):
        # n=1,2,3,4
        self.write('CHAN'+str(n)+':SCAL '+str(scal))
        return

    def SetVoltRange(self,rang,n=1):
        # n=1,2,3,4
        self.write('CHAN'+str(n)+':RANG '+str(rang))
        return

    def SetTimeScale(self,scal):
        self.write(':TIM:SCAL '+str(scal))
        return

    def SetNumPoints(self,npoints):
        self.write(':ACQ:MDEPT '+str(npoints))

    def GetSampleRate(self):
        return float(self.query(':ACQ:SRAT?'))

    def GetTimeScale(self):
        return float(self.query(':TIM:SCAL?'))

    def SetMemoryDepth(self,mdep):
        self.write(':ACQ:MDEP '+str(mdep))
        return

    def GetMemoryDepth(self):
        return self.query(':ACQ:MDEP?')

    def GetTrace(self,ch=1):
        time.sleep(1)
        tscale = self.GetTimeScale()
        time.sleep(tscale*12)
        self.write(':WAV:SOUR CHAN'+str(ch))
        self.write('WAV:MODE NORM')
        self.write('WAV:FORM BYTE')

        xinc = float(self.query('WAV:XINC?'))
        yinc = float(self.query('WAV:YINC?'))
        yori = float(self.query('WAV:YOR?'))
        yref = float(self.query('WAV:YREF?'))
        
        dat = self.write(':WAV:DATA?')
        output = self.dev.read_raw()
        npoints = int(output[2:11].decode('ascii'))
        print(npoints)
        output = [(x - yori - yref) * yinc for x in output[11:] ]
        output = np.array(output[:npoints])
        xs = np.linspace(0,tscale*12,len(output))
        return xs,output

    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass

    '''
    def ReadWaveData(self,n=1,mdep=3e6):
        self.write('STOP')
        self.write(':WAV:SOUR CHAN'+str(n))
        self.write('STOP')
        try:
            nsamp = int(self.query('ACQ:MDEP?'))
        except:
            #nsamp = input("Enter memory depth: ")
            #nsamp = int(nsamp)
            self.SetMemoryDepth(mdep)
            nsamp = int(mdep)
        self.write('WAV:MODE RAW')
        self.write('WAV:FORM BYTE')
        nmax = 250000  #Max read points 250000 when bytes
        nreads = math.ceil(nsamp/nmax)

        # to scale the data properly
        xinc = float(self.query('WAV:XINC?'))
        yinc = float(self.query('WAV:YINC?'))
        yori = float(self.query('WAV:YOR?'))
        yref = float(self.query('WAV:YREF?'))
        srate = float(self.query('ACQuire:SRATe?'))

        data = []
        for i in range(nreads):
            self.write('WAV:STAR {}'.format(i*nmax+1) )
            if i == nreads-1:
                self.write('WAV:STOP {}'.format(nsamp))
            else:
                self.write('WAV:STOP {}'.format((i+1)*nmax))
            self.write('WAV:DATA?')
            output = self.dev.read_raw()
            npoints = int(output[2:11].decode('ascii'))
            print(i,npoints)
            output = [(x - yori - yref) * yinc for x in output[11:] ]
            output = output[:npoints]
            data.append(output)
        data = np.asarray(data).flatten()
        return data
    '''



