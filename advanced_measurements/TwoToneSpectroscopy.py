"""Methods to perform Two Tone Spectroscopy

The methods included here allow one to setup a 4 port VNA to do a two tone measurement
The intended workflow is:

- First run :any:`TwoToneSetup` to set up the channels
- Then run :any:`TwoToneProbeForMin` to scan for the minimum
- ...

"""
import numpy as np
import pandas as pd
from collections import OrderedDict

class PNA_rfsource():
    """class that allows one to use the third port of the
    PNA as a RF source"""
    def __init__(self, pna, N_pow,N_rang):
        super().__init__()
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


def TwoToneSetup(pna,
    f_probe_start,
    f_probe_stop,
    f_probe_points,
    probe_ifbw,
    probe_power,
    f_pump_start,
    f_pump_stop,
    f_pump_points,
    pump_ifbw,
    pump_power,
    searchtype = 'MAX'):
    """Two tone setup

    Performs the basic pna setup on the given pna device (usually a PNAN5222A)

    Paramters
    ---------
    pna : stlab.devices.PNAN5222A.PNA5222A
        Pna device to setup.  Should already have been instantiated
    f_probe_start : float
        Probe start frequency in Hz
    f_probe_stop : float
        Probe stop frequency in Hz
    f_probe_points : int
        Number of probe points
    probe_ifbw : float
        Probe IF bandwidth in Hz
    probe_power : float
        Probe power in dBm
    f_pump_start : float
        Pump start frequency in Hz
    f_pump_stop : float
        Pump stop frequency in Hz
    pump_ifbw : float
        Pump IF bandwidth in Hz
    pump_power : float
        Pump power in dBm
    searchtype : {'MAX,MIN'}, optional
        If set to 'MAX' will search for a maximum in the initial probe sweep (readout cavity frequency).
        If set to 'MIN' will search for a minimum instead.

    """
    pna.write('*RST')      #stop any OPCs and go to preset (same as 'Preset' button) (overkill) (better)
    pna.write('SYST:FPR')  #do reset with all windows and traces deleted


    #setup two displays
    pna.write("DISP:WIND1:STATE ON")
    pna.write("DISP:WIND2:STATE ON")

    ###setup probe scan (magnitude)
    pna.write("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
    pna.write("DISP:WIND1:TRACE1:FEED 'CH1_S21_S1'")
    pna.write("CALC1:PAR:SEL 'CH1_S21_S1'")
    pna.write("CALC1:FORM MLOG")

    #setup triggering per channel
    pna.write("INIT:CONT OFF")
    pna.write("SENS1:SWE:MODE HOLD")
    pna.write("TRIG:SCOP CURR")


    ###setup probe scan more
    pna.write("SENS:FREQ:START %s" % (f_probe_start))
    pna.write("SENS:FREQ:STOP %s" % (f_probe_stop))
    pna.write("SENS:SWE:POIN %s" % (f_probe_points))
    pna.write("SENS:BWID %s" % (probe_ifbw))
    pna.write("SOUR:POW1 %s" %(probe_power))

    #do settings for Marker for the probe
    pna.write("CALC1:MARK:REF ON")
    pna.write("CALC1:MARK:REF:X " + str(f_probe_start))
    pna.write("CALC1:MARK1 ON")
    pna.write("CALC1:MARK1:FUNC {}".format(searchtype))
    pna.write("CALC1:MARK1:FUNC:TRAC ON")
    pna.write("CALC1:MARK1:DELT ON")
    pna.write("CALC1:MARK2 ON")
    pna.write("CALC1:MARK2:FUNC {}".format(searchtype))
    pna.write("CALC1:MARK2:FUNC:TRAC ON")



    ###setup two tone scan
    pna.write("CALC2:PAR:DEF:EXT 'CH2_S21_S1', 'B,1'")
    pna.write("DISP:WIND2:TRACE1:FEED 'CH2_S21_S1'")
    pna.write("CALC2:PAR:SEL 'CH2_S21_S1'")
    pna.write("CALC2:FORM MLOG")
    ##
    pna.write("SENS2:FREQ:START %s" % (f_pump_start))
    pna.write("SENS2:FREQ:STOP %s" % (f_pump_stop))
    pna.write("SENS2:SWE:POIN %s" % (f_pump_points))
    pna.write("SENS2:BWID %s" % (pump_ifbw))

    ##
    ##
    pna.write("SENS2:FOM:STATE 1")      #switch on Frequency Offset Module
    pna.write("SENS2:FOM:RANG3:COUP 0")     #decouple Receivers
    pna.write("SENS2:FOM:RANG2:COUP 0")     #decouple Source
    ##
    pna.write("SENS2:FOM:RANG3:SWE:TYPE CW")    #set Receivers in CW mode
    pna.write("SENS2:FOM:RANG2:SWE:TYPE CW")    #set Source in CW mode
    ##
    pna.write("SENS2:FOM:RANG3:FREQ:CW %s" %(f_probe_start)) #set cw freq to receivers
    pna.write("SENS2:FOM:RANG2:FREQ:CW %s" %(f_probe_start)) #set cw freq to source1
    ##
    pna.write("SENS2:FOM:DISP:SEL 'Primary'")       #set x-axis to primary
    ##
    pna.write("SOUR2:POW:COUP 0")                   #decouple powers
    pna.write("SOUR2:POW1 %s" %(probe_power))
    pna.write("SOUR2:POW3 %s" %(pump_power))
    pna.write("SOUR2:POW3:MODE ON")                 #switch on port3

    pna.write("CALC2:MARK1 ON")
    if searchtype == 'MAX':
        pna.write("CALC2:MARK1:FUNC MIN")
    elif searchtype == 'MIN':
        pna.write("CALC2:MARK1:FUNC MAX")
    else:
        raise ValueError('Bad search type')
    pna.write("CALC2:MARK1:FUNC:TRAC ON")

def TwoToneProbeSet(pna,searchtype='MAX'):

    #set continuous off
    pna.write("SENS1:SWE:MODE HOLD")
    pna.write("INIT:CONT OFF")

    # Trigger top screen measurement
    pna.write("INIT1:IMM" )
    pna.query('*OPC?')

    # Autoscale and copy scale to lower screen
    pna.write('DISP:WIND1:Y:AUTO')

    pna.write('DISP:WIND2:TRAC:Y:PDIV  %s' %eval(pna.query('DISP:WIND1:TRAC:Y:PDIV?')))
    pna.write('DISP:WIND2:TRAC:Y:RLEV  %s' %eval(pna.query('DISP:WIND1:TRAC:Y:RLEV?')))
    pna.write('DISP:WIND2:TRAC:Y:RPOS  %s' %eval(pna.query('DISP:WIND1:TRAC:Y:RPOS?')))

    pna.write("CALC1:MARK2:FUNC {}".format(searchtype))

    return eval(pna.query("CALC1:MARK2:X?"))

def TwoToneSetPumpPower(pna,pump_power):
    pna.write("SOUR2:POW3 %s" %(pump_power))

def TwoToneSetProbeFrequency(pna,frequency):
    pna.write("SENS2:FOM:RANG3:FREQ:CW %s" %(frequency)) #set cw freq to receivers
    pna.write("SENS2:FOM:RANG2:FREQ:CW %s" %(frequency)) #set cw freq to source1


def TwoToneMeasure(pna):
    # Trigger
    pna.write("INIT2:IMM")
    pna.query('*OPC?')
    pna.write('DISP:WIND2:Y:AUTO')

    # pars,parnames = pna.GetTraceNames()
    # pna.SetActiveTrace(pars[0])
    pp = 'CH1_S21_S1'
    traces = ['CH1_S21_S1','CH2_S21_S1']
    result = []
    for i,pp in enumerate(traces):
        pna.SetActiveTrace(pp,ch=i+1)
        names = ['Frequency (Hz)']
        alltrc = [pna.GetFrequency(ch=i+1)]
        names.append('%sre ()' % pp)
        names.append('%sim ()' % pp)
        names.append('%sdB (dB)' % pp)
        names.append('%sPh (rad)' % pp)
        yyre,yyim = pna.GetTraceData(i+1)
        alltrc.append(yyre)
        alltrc.append(yyim)
        yydb = 20.*np.log10( np.abs(yyre+1j*yyim) )
        yyph = np.unwrap(np.angle(yyre+1j*yyim))
        alltrc.append(yydb)
        alltrc.append(yyph)
        mydict = OrderedDict()
        for name,data in zip(names,alltrc):
            mydict[name]=data
        mydict = pd.DataFrame(mydict)
        result.append(mydict)

    return result

def TwoToneSourcesOff(pna):
    pna.write('SOUR1:POW1:MODE OFF')
    pna.write('SOUR1:POW3:MODE OFF')
    pna.write('SOUR2:POW1:MODE OFF')
    pna.write('SOUR2:POW3:MODE OFF')