"""PNA power sweep

Example script to perform a series of frequency traces on a PNA as a function of input power

"""

import stlab
import numpy as np

prefix = 'B' #prefix for measurement folder name.  Can be anything or empty
idstring = 'LT130W2_6I_b_powersweep' #Additional info included in measurement folder name.  Can be anything or empty

pna = stlab.adi(addr='TCPIP::192.168.1.221::INSTR',reset=False,verb=True) #Initialize device communication and reset

pna.SetRange(5.5e9,6.5e9) #Set frequency range in Hz
pna.SetIFBW(10.) #Set IF bandwidth in Hz
pna.SetPoints(1001) #Set number of frequency points

powstart = -30.
powstop = 30.
steps = 61
powers = np.linspace(powstart,powstop,steps) #generate power sweep steps

myfile = stlab.newfile(prefix,idstring,autoindex=True)
for i,rfpower in enumerate(powers):
    pna.SetPower(rfpower) #set pna power
    data = pna.MeasureScreen_pd() #Trigger 2 port measurement and retrieve data in Re,Im format.  Returns OrderedDict
    stlab.saveframe(myfile, data) #Save measured data to file.  Written as a block for spyview.
    #Create metafile for spyview at each measurement step
    stlab.metagen.fromarrays(myfile,data['Frequency (Hz)'],powers[0:i+1],xtitle='Frequency (Hz)',ytitle='Power (dB)',colnames=data.keys())
myfile.close() #Close file

