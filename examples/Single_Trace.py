import stlab
from stlab.devices.PNAN5221A import PNAN5221A as pnaclass #Import device driver for your desired PNA
import numpy as np

prefix = 'M1' #prefix for measurement folder name.  Can be anything or empty
idstring = 'New_Triton_Wires_Open_B2C5_B2C6' #Additional info included in measurement folder name.  Can be anything or empty

pna = pnaclass(addr='TCPIP::192.168.1.105::INSTR',reset=False,verb=True) #Initialize device communication and reset

data = pna.MeasureScreen() #Trigger 2 port measurement and retrieve data in Re,Im format.  Returns OrderedDict
rfpower = pna.GetPower()
data.addparcolumn('Power (dBm)',rfpower)
myfile = stlab.newfile(prefix,idstring,data.keys())
stlab.savedict(myfile, data) #Save measured data to file.  Written as a block for spyview.
#Create metafile for spyview at each measurement step
stlab.metagen.fromarrays(myfile,data['Frequency (Hz)'],[0,1],xtitle='Frequency (Hz)',ytitle='None',colnames=data.keys())
myfile.close() #Close file

