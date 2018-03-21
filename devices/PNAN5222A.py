import visa
import numpy as np
import time
from stlab.devices.instrument import instrument
from stlab.devices.PNAN5221A import PNAN5221A
from stlab.utils.stlabdict import stlabdict

def numtostr(mystr):
    return '%20.15e' % mystr
#    return '%20.10f' % mystr

class PNAN5222A(PNAN5221A):
    def __init__(self,addr='TCPIP::192.168.1.42::INSTR',reset=True,verb=True):
        super().__init__(addr,reset,verb)

    def TwoPortSetup(self,port1=1,port2=2):
        ports = [port1,port2]
        trcnames = self.GetTrcNames()
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
        self.write("INIT1:IMM" )    

        
        while True:
            time.sleep(0.01)
            try:
                a=eval(self.query('*OPC?;'))
                break
            except(KeyboardInterrupt, SystemExit):
                raise

        self.write("CALC1:MARK2:FUNC MIN")
        return eval(self.query("CALC1:MARK2:X?"))


    def TwoToneSetProbeFrequency(self,frequency):
        self.write("SENS2:FOM:RANG3:FREQ:CW %s" %(frequency)) #set cw freq to receivers
        self.write("SENS2:FOM:RANG2:FREQ:CW %s" %(frequency)) #set cw freq to source1

    def TwoToneMeasure(self):
        # Trigger
        self.write("INIT2:IMM")
        self.query('*OPC?')

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
            result.append(mydict)

        return result

