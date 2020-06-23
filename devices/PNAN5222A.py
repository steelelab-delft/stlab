import visa
import numpy as np
import time
from stlab.devices.instrument import instrument
from stlab.devices.PNAN5221A import PNAN5221A
from stlabutils.stlabdict import stlabdict
import pandas as pd

def numtostr(mystr):
    return '%20.15e' % mystr

class PNA_rfsource(object):
    """class that allows one to use the third port of the
    PNA as a RF source"""
    def __init__(self, pna,N_pow,N_rang):
        super(PNA_rfsource, self).__init__()
        self.pna = pna
        self.N_pow = N_pow
        self.N_rang = N_rang

    def RFoff(self):
        self.pna.write("SOUR:POW%d:MODE OFF"%self.N_pow)
    def RFon(self, ):
        self.pna.write("SOUR:POW%d:MODE ON"%self.N_pow)
    def EXTref(self):
        pass
    def INTref(self):
        pass
    def setCWpower(self,power):
        self.pna.write("SOUR:POW%d %s" %(self.N_pow,power))
    def setCWfrequency(self,frequency):
        self.pna.write("SENS:FOM:RANG%d:FREQ:CW %s" %(self.N_rang,frequency))


class PNAN5222A(PNAN5221A):
    def __init__(self,
                 addr='TCPIP::192.168.1.216::INSTR',
                 reset=True,
                 verb=True):
        super().__init__(addr,reset,verb)


    #******************************************************************************************
    #******************************************************************************************
    #******       Two tone spectroscopy funcitons.  Should be removed to TwoToneSpectroscopy.py
    #******************************************************************************************
    #******************************************************************************************
    #******************************************************************************************

    def create_source(self):

        self.write("SENS1:FOM:STATE 1")      #switch on Frequency Offset Module
        self.write("SENS1:FOM:RANG4:COUP 0")           #decouple source
        self.write("SENS1:FOM:RANG4:SWE:TYPE CW")       #set Source in CW mode
        self.write("SOUR:POW:COUP 0")                   #decouple powers

        return PNA_rfsource(self,N_pow = 3,N_rang = 4)

    def create_two_sources(self):
        self.reset()
        self.SetContinuous(False)
        self.ClearAll()
        self.AddTraces('S21')

        #switch on Frequency Offset Module
        # to allow decoupling of the ports
        # from the frequency sweep
        self.write("SENS:FOM:STATE 1")

        # RANG corresponds to the row when one
        # opens the frequency offset module on the PNA
        # RANG1: primary
        # RANG2: source (1)
        # RANG3: receivers
        # RANG4: source 2
        # We want to decouple everything
        self.write("SENS:FOM:RANG2:COUP 0")           #decouple source
        self.write("SENS:FOM:RANG3:COUP 0")           #decouple source
        self.write("SENS:FOM:RANG4:COUP 0")           #decouple source

        # This decouples all the sources in terms of power
        self.write("SOUR:POW:COUP 0")

        # Turn off the power on the one that
        # is on by default after reset
        self.write("SOUR:POW1:MODE OFF")
        self.write("SOUR:POW2:MODE OFF")
        self.write("SOUR:POW3:MODE OFF")
        self.write("SOUR:POW4:MODE OFF")

        # RANG2 and RANG4 are the sources, corresponding
        # to ports 1 and 3 respectively,
        # we set both to CW mode
        self.write("SENS:FOM:RANG2:SWE:TYPE CW")
        self.write("SENS:FOM:RANG4:SWE:TYPE CW")

        return PNA_rfsource(self,N_pow = 1,N_rang = 2), PNA_rfsource(self,N_pow = 3,N_rang = 4)


    def TwoToneSetup(self,
        f_probe_start,
        f_probe_stop,
        f_probe_points,
        probe_ifbw,
        probe_power,
        f_pump_start,
        f_pump_stop,
        f_pump_points,
        pump_ifbw,
        pump_power):
        self.write('*RST')      #stop any OPCs and go to preset (same as 'Preset' button) (overkill) (better)
        self.write('SYST:FPR')  #do reset with all windows and traces deleted


        #setup two displays
        self.write("DISP:WIND1:STATE ON")
        self.write("DISP:WIND2:STATE ON")

        ###setup probe scan (magnitude)
        self.write("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
        self.write("DISP:WIND1:TRACE1:FEED 'CH1_S21_S1'")
        self.write("CALC1:PAR:SEL 'CH1_S21_S1'")
        self.write("CALC1:FORM MLOG")

        #setup triggering per channel
        self.write("INIT:CONT OFF")
        self.write("SENS1:SWE:MODE HOLD")
        self.write("TRIG:SCOP CURR")


        ###setup probe scan more
        self.write("SENS:FREQ:START %s" % (f_probe_start))
        self.write("SENS:FREQ:STOP %s" % (f_probe_stop))
        self.write("SENS:SWE:POIN %s" % (f_probe_points))
        self.write("SENS:BWID %s" % (probe_ifbw))
        self.write("SOUR:POW1 %s" %(probe_power))

        #do settings for Marker for the probe
        self.write("CALC1:MARK:REF ON")
        self.write("CALC1:MARK:REF:X " + str(f_probe_start))
        self.write("CALC1:MARK1 ON")
        self.write("CALC1:MARK1:FUNC MIN")
        self.write("CALC1:MARK1:FUNC:TRAC ON")
        self.write("CALC1:MARK1:DELT ON")
        self.write("CALC1:MARK2 ON")
        self.write("CALC1:MARK2:FUNC MIN")
        self.write("CALC1:MARK2:FUNC:TRAC ON")



        ###setup two tone scan
        self.write("CALC2:PAR:DEF:EXT 'CH2_S21_S1', 'B,1'")
        self.write("DISP:WIND2:TRACE1:FEED 'CH2_S21_S1'")
        self.write("CALC2:PAR:SEL 'CH2_S21_S1'")
        self.write("CALC2:FORM MLOG")
        ##
        self.write("SENS2:FREQ:START %s" % (f_pump_start))
        self.write("SENS2:FREQ:STOP %s" % (f_pump_stop))
        self.write("SENS2:SWE:POIN %s" % (f_pump_points))
        self.write("SENS2:BWID %s" % (pump_ifbw))

        ##
        ##
        self.write("SENS2:FOM:STATE 1")      #switch on Frequency Offset Module
        self.write("SENS2:FOM:RANG3:COUP 0")     #decouple Receivers
        self.write("SENS2:FOM:RANG2:COUP 0")     #decouple Source
        ##
        self.write("SENS2:FOM:RANG3:SWE:TYPE CW")    #set Receivers in CW mode
        self.write("SENS2:FOM:RANG2:SWE:TYPE CW")    #set Source in CW mode
        ##
        self.write("SENS2:FOM:RANG3:FREQ:CW %s" %(f_probe_start)) #set cw freq to receivers
        self.write("SENS2:FOM:RANG2:FREQ:CW %s" %(f_probe_start)) #set cw freq to source1
        ##
        self.write("SENS2:FOM:DISP:SEL 'Primary'")       #set x-axis to primary
        ##
        self.write("SOUR2:POW:COUP 0")                   #decouple powers
        self.write("SOUR2:POW1 %s" %(probe_power))
        self.write("SOUR2:POW3 %s" %(pump_power))
        self.write("SOUR2:POW3:MODE ON")                 #switch on port3

        self.write("CALC2:MARK1 ON")
        self.write("CALC2:MARK1:FUNC MAX")
        self.write("CALC2:MARK1:FUNC:TRAC ON")

    def TwoToneProbeForMin(self):

        #set continuous off
        self.write("SENS1:SWE:MODE HOLD")
        self.write("INIT:CONT OFF")

        # Trigger top screen measurement
        self.write("INIT1:IMM" )
        self.query('*OPC?')

        # Autoscale and copy scale to lower screen
        self.write('DISP:WIND1:Y:AUTO')

        self.write('DISP:WIND2:TRAC:Y:PDIV  %s' %eval(self.query('DISP:WIND1:TRAC:Y:PDIV?')))
        self.write('DISP:WIND2:TRAC:Y:RLEV  %s' %eval(self.query('DISP:WIND1:TRAC:Y:RLEV?')))
        self.write('DISP:WIND2:TRAC:Y:RPOS  %s' %eval(self.query('DISP:WIND1:TRAC:Y:RPOS?')))

        self.write("CALC1:MARK2:FUNC MIN")

        return eval(self.query("CALC1:MARK2:X?"))

    def TwoToneProbeForMax(self):

        #set continuous off
        self.write("SENS1:SWE:MODE HOLD")
        self.write("INIT:CONT OFF")

        # Trigger top screen measurement
        self.write("INIT1:IMM" )
        self.query('*OPC?')

        # Autoscale and copy scale to lower screen
        self.write('DISP:WIND1:Y:AUTO')

        self.write('DISP:WIND2:TRAC:Y:PDIV  %s' %eval(self.query('DISP:WIND1:TRAC:Y:PDIV?')))
        self.write('DISP:WIND2:TRAC:Y:RLEV  %s' %eval(self.query('DISP:WIND1:TRAC:Y:RLEV?')))
        self.write('DISP:WIND2:TRAC:Y:RPOS  %s' %eval(self.query('DISP:WIND1:TRAC:Y:RPOS?')))

        self.write("CALC1:MARK2:FUNC MAX")

        return eval(self.query("CALC1:MARK2:X?"))

    def TwoToneSetPumpPower(self,pump_power):
        self.write("SOUR2:POW3 %s" %(pump_power))

    def TwoToneSetProbeFrequency(self,frequency):
        self.write("SENS2:FOM:RANG3:FREQ:CW %s" %(frequency)) #set cw freq to receivers
        self.write("SENS2:FOM:RANG2:FREQ:CW %s" %(frequency)) #set cw freq to source1

    def TwoToneMeasure(self):
        # Trigger
        self.write("INIT2:IMM")
        self.query('*OPC?')
        self.write('DISP:WIND2:Y:AUTO')

        # pars,parnames = self.GetTraceNames()
        # self.SetActiveTrace(pars[0])
        pp = 'CH1_S21_S1'
        traces = ['CH1_S21_S1','CH2_S21_S1']
        result = []
        for i,pp in enumerate(traces):
            self.SetActiveTrace(pp,ch=i+1)
            names = ['Frequency (Hz)']
            alltrc = [self.GetFrequency(ch=i+1)]
            names.append('%sre ()' % pp)
            names.append('%sim ()' % pp)
            names.append('%sdB (dB)' % pp)
            names.append('%sPh (rad)' % pp)
            yyre,yyim = self.GetTraceData(i+1)
            alltrc.append(yyre)
            alltrc.append(yyim)
            yydb = 20.*np.log10( np.abs(yyre+1j*yyim) )
            yyph = np.unwrap(np.angle(yyre+1j*yyim))
            alltrc.append(yydb)
            alltrc.append(yyph)
            mydict = stlabdict()
            for name,data in zip(names,alltrc):
                mydict[name]=data
            mydict = pd.DataFrame(mydict)
            result.append(mydict)

        return result

    def TwoToneSourcesOff(self):
        self.write('SOUR1:POW1:MODE OFF')
        self.write('SOUR1:POW3:MODE OFF')
        self.write('SOUR2:POW1:MODE OFF')
        self.write('SOUR2:POW3:MODE OFF')

    def GetMin(self):
        self.write("CALC:MARK1 ON")             # Turn on marker
        self.write("CALC:MARK1:FUNC MIN")       # Set to minimum
        self.write("CALC:MARK1:FUNC:TRAC ON")   # Don't know what this is but dosnt work without
        self.query('*OPC?')                     # Wait
        return eval(self.query("CALC:MARK1:X?"))# return minimum

    def GetMax(self):
        self.write("CALC:MARK1 ON")             # Turn on marker
        self.write("CALC:MARK1:FUNC MAX")       # Set to maximum
        self.write("CALC:MARK1:FUNC:TRAC ON")   # Don't know what this is but dosnt work without
        self.query('*OPC?')                     # Wait
        return eval(self.query("CALC:MARK1:X?"))# return maximum



    #******************************************************************************************
    #******************************************************************************************
    #******************************************************************************************
    #******************************************************************************************
    #For Segment sweeps

    def DelAllSegm(self):
        self.write('SENS:SEGM:DEL:ALL')
        return

    def AddSegm(self,snum=1):
        self.write('SENS:SEGM{}:ADD'.format(snum))
        return

    def SetSweepType(self, tt = 'LIN'): #Possible options: LINear | LOGarithmic | POWer | CW | SEGMent | PHASe
        self.write('SENS:SWE:TYPE {}'.format(tt))
        return

    def SetArbitrarySegSweep(self, on=True):
        if on:
            self.write('SENS:SEGM:ARB ON')
        else:
            self.write('SENS:SEGM:ARB OFF')

    def SetSegmStart(self, x, snum = 1):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM{}:FREQ:STAR {}'.format(snum,mystr)
        self.write(mystr)

    def SetSegmEnd(self, x, snum = 1):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM{}:FREQ:STOP {}'.format(snum,mystr)
        self.write(mystr)

    def SetSegmPoints(self, x, snum=1):
        mystr = '%d' % x
        mystr = 'SENS:SEGM{}:SWE:POIN {}'.format(snum,mystr)
        self.write(mystr)

    def SetSegmRange(self, start, end):
        self.SetSegmStart(start)
        self.SetSegmEnd(end)

    def SetSegmState(self, state='ON'): #'ON' or 'OFF'
        self.write('SENS:SEGM {}'.format(state))
        return

    def GetSweepTime(self):
        result = self.query('SENSe:SWEep:TIME?')
        return float(result)

    def TwoPortSetup(self,port1=1,port2=2):
        ports = [port1,port2]
        trcnames = self.GetTraceNames()
        measnames = ['S%d%d' % (b,a) for a in ports for b in ports]
        if trcnames == measnames:
            return
        self.ClearAll()
        self.write('DISP:WIND1 ON')
        tracenames = ['CH1_S%d%d' % (b,a) for a in ports for b in ports]
        for i,(meas,trc) in enumerate(zip(measnames,tracenames)):
            self.write("CALC:PAR:DEF:EXT '%s', '%s'" % (trc,meas))
            self.write("DISP:WIND:TRAC%d:FEED '%s'" % (i+1,trc))
        self.write('DISP:WIND:TRAC2:MOVE 2')
        self.write('DISP:WIND:TRAC3:MOVE 2')

    def Average(self,N_averages=5):
        self.write('SENS:AVER:COUN %d'%N_averages)
        self.write('SENS:AVER ON')
        self.write('SENS:AVER:CLEAR')
        naver = int(self.query('SENS:AVER:COUN?'))
        for j in range(naver-1):
            self.Trigger()
        self.write('SENS:AVER OFF')

    def SetSweepDelay(self,tt):
        self.write('SENS:SWE:DWEL:SDEL {}'.format(tt))
        return

    #Not currently working for segments
    '''
    def SetSegmIFBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM:BWID '+mystr
        self.write(mystr)
    def SetSegmPower(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:SEGM:POW '+mystr
        self.write(mystr)
    '''



