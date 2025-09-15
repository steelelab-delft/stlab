import numpy as np
from .instrument import instrument
import time


def numtostr(mystr):
    return '%12.8e' % mystr


class Keysight_B2961A(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.50::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.dev.timeout = None
        self.id()

    #OLD READ METHOD WITH OPC... NOT SURE IF NECESSARY. IF COMMENTED WILL USE INHERITED FROM instrument
    '''
    def write(self,mystr):
        writestr = mystr+';*OPC?'
        self.dev.query(writestr)
        if self.verb:
            print(writestr)
    '''

    def SetModeCurrent(self):
        self.write(':SOUR:FUNC:MODE CURR')

    def SetModeVoltage(self):
        self.write(':SOUR:FUNC:MODE VOLT')

    def GetMode(self):
        mode = self.query(':SOUR:FUNC:MODE?')
        mode = mode.strip()
        return mode

    def SetOutputOn(self):
        self.write(':OUTP ON')

    def SetOutputOff(self):
        self.write(':OUTP OFF')

    def SetCurrent(self, curr):
        mystr = numtostr(curr)
        mystr = ':SOUR:CURR ' + mystr
        self.write(mystr)

    def SetVoltage(self, curr):
        mystr = numtostr(curr)
        mystr = ':SOUR:VOLT ' + mystr
        self.write(mystr)

    def SetComplianceVoltage(self, volt):
        mystr = numtostr(volt)
        mystr = ':SENS:VOLT:PROT ' + mystr
        self.write(mystr)

    def SetComplianceCurrent(self, curr):
        mystr = numtostr(curr)
        mystr = ':SENS:CURR:PROT ' + mystr
        self.write(mystr)

    def GetCurrent(self):
        mystr = ':MEAS:CURR?'
        curr = self.query(mystr)
        curr = float(curr)
        return curr

    def GetVoltage(self):
        mystr = ':MEAS:VOLT?'
        volt = self.query(mystr)
        volt = float(volt)
        return volt

    def GetVoltCurr(self):
        mystr = 'FORM:ELEM:SENS VOLT,CURR'
        self.write(mystr)
        mystr = ':MEAS?'
        outstr = self.query(mystr)
        data = np.array(list(map(float, outstr.split(','))))
        return (data[0], data[1])

    def RampVoltage(
            self, mvoltage, tt=5., steps=100
    ):  #To ramp voltage over 'tt' seconds from current DAC value.
        v0 = self.GetVoltage()
        if np.abs(mvoltage - v0) < 1e-3:
            self.SetVoltage(mvoltage)
            return
        voltages = np.linspace(v0, mvoltage, steps)
        twait = tt / steps
        for vv in voltages:
            self.SetVoltage(vv)
            time.sleep(twait)

    def RampCurrent(
            self, curr, tt=5., steps=100, tol=1e-3
    ):  #To ramp current over 'tt' seconds from current DAC value.
        I0 = self.GetCurrent()
        if np.abs(curr - I0) < tol:
            self.SetCurrent(curr)
            return
        currents = np.linspace(I0, curr, steps)
        twait = tt / steps
        for ii in currents:
            self.SetCurrent(ii)
            time.sleep(twait)

    def RampCurrent_step_speed(
            self, curr, step, speed, verb=True
    ):  # To ramp current at a given speed (A/s) from current DAC value.
        # speed does not account for python overhead which depends on step
        # in practice we find:
        # - 0.01uA steps at 0.5uA/s - 30s to make 10uA - 1.5x overhead
        # - ...
        self.SetModeCurrent()
        # TO DO: could add a check to see if output is on and set current to 0 if not
        self.SetOutputOn() 
        I0 = self.GetCurrent()
        
        Nsteps = int(np.ceil(np.abs(curr - I0) / step))
        total_time = np.abs(curr - I0) / speed
        twait = total_time / Nsteps
        if verb is True:
            print('RAMPING CURRENT from %.3f uA to %.3f uA in %d steps (ETA %.2f s) ' %
                  (I0*1e6, curr*1e6, Nsteps, total_time), end='', flush=True)
            
        currents = np.linspace(curr, I0, Nsteps)[::-1]   # Reverse order to end at desired current
        t0 = time.time()
        for ii, current in enumerate(currents):
            if verb is True and Nsteps >= 10 and ii > 1:   # Printing progress only if at least 10 steps
                if not ii % int(Nsteps/10):
                    print('.', end='', flush=True)
            self.SetCurrent(current)
            time.sleep(twait)
        if verb is True:
            print(' DONE in %.2f s.' % (time.time() - t0) )

    def SetSweep(self, type='SING'):
        mode = self.GetMode()
        self.write('{}:MODE SWE'.format(mode))
        self.write('SWE:DIR UP')
        self.write('SWE:STA {}'.format(type))
        self.write('TRIG:SOUR AINT')
        return

    def SetStartStop(self, start, stop):
        mode = self.GetMode()
        self.write('{}:STAR {}'.format(mode, start))
        self.write('{}:STOP {}'.format(mode, stop))
        self.write('SWE:RANG BEST')

    def SetPoints(self, nn):
        self.write('SWE:POIN {}'.format(nn))
        swetype = (self.query('SWE:STA?')).strip()
        if swetype == 'DOUB':
            self.write('TRIG:COUN {}'.format(2 * nn))
        else:
            self.write('TRIG:COUN {}'.format(nn))
        return

    def RunSweep(self):
        self.SetOutputOn()
        self.query('INIT; *OPC?')
        x = self.query('FETC:ARR:CURR?')
        y = self.query('FETC:ARR:VOLT?')
        self.SetOutputOff()
        x = x.strip().split(',')
        y = y.strip().split(',')
        x = [float(xx) for xx in x]
        y = [float(xx) for xx in y]
        return y, x  #Return V,I regardless of sweep parameter

    def SetNPLC(self, nn):
        mode = self.GetMode()
        self.write('SENS:{}:NPLC {}'.format(mode, nn))
        return

    def Set4Wire(self, ss=True):
        if ss:
            self.write('SENS:REM ON')
        else:
            self.write('SENS:REM OFF')
        return

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass


'''    
dev.write('SWE:RANG BEST')
dev.write('SWE:DIR UP')
dev.write('SWE:SPAC LIN')
dev.write('SWE:STA DOUB')
dev.write('SENS:FUNC "VOLT"')
dev.write('SENS:VOLT:RANG 1.')
dev.write('SENS:VOLT:NPLC 1')
dev.write('SENS:VOLT:PROT 1')
dev.write('TRIG:SOUR AINT')
dev.write('TRIG:COUN 1002')
dev.write('OUTP ON')
dev.query('INIT; *OPC?')
x = dev.query('FETC:ARR:CURR?')
y = dev.query('FETC:ARR:VOLT?')
dev.write('OUTP OFF')
x = x.strip().split(',')
y = y.strip().split(',')
x=[float(xx) for xx in x]
y=[float(xx) for xx in y]
plt.plot(x,y)
plt.show()
'''
