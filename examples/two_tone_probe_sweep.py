import stlab
from stlab.devices.PNAN5222A import PNAN5222A
import numpy as np

pna = PNAN5222A(addr='TCPIP::192.168.1.221::INSTR',reset=True,verb=True) #Initialize device communication and reset
# setup measurement
pna.reset()
pna.SetContinuous(False)
pna.ClearAll()
pna.AddTraces('S21')
# we use port 3 of the VNA as a RF source
pump = pna.create_source() 

f_res = 5e9

prefix = '' #prefix for measurement folder name.  Can be anything or empty
idstring = 'two_tone_probe_sweep'+str(f_res) #Additional info included in measurement folder name.  Can be anything or empty


# setup probe sweep
probe_range = 3e3
pna.SetRange(f_res+probe_range, f_res-probe_range)
pna.SetIFBW(100) #Set IF bandwidth in Hz
pna.SetPoints(10e3) #Set number of frequency points
pna.SetPower(-20) #set pna power

# Set pump powers
powstart = 30
powstop = -15
steps = -1
pump_powers = np.arange(powstart,powstop,steps) #generate power sweep steps

# Set pump delta freqs
dstart = -50e6
dstop = -1e6
steps = 150e3
delta_fs = np.arange(dstart,dstop,steps) #generate power sweep steps
pump_freqs = delta_fs + f_res


for i,rfpower in enumerate(pump_powers):
    pump.setCWpower(rfpower) #set pna power
    
    for j, freq in enumerate(pump_freqs):
        print('Power %d/%d, Freq %d/%d'%(i,len(pump_powers),j,len(pump_freqs)))
        pump.setCWfrequency(freq)
        pump.RFon()


        data = pna.MeasureScreen() #Trigger 2 port measurement and retrieve data in Re,Im format.  Returns OrderedDict
        pna.AutoScaleAll()
        #Add Columns for S parameters in dB
        if i==0 and j==0: #if on first measurement, create new measurement file and folder using titles extracted from measurement
            myfile = stlab.newfile(prefix,idstring,data.keys())
        stlab.savedict(myfile, data) #Save measured data to file.  Written as a block for spyview.
        #Create metafile for spyview at each measurement step
        stlab.metagen.fromarrays(myfile,
                (data['Frequency (Hz)']-f_res)/1e3,
                pump_powers[0:i+1],
                pump_freqs[0:j+1],
                xtitle='Detuning (kHz)',
                ytitle='Pump power (dB)',
                ztitle='Pump freq (Hz)',
                colnames=data.keys())
myfile.close() #Close file


