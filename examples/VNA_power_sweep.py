import stlab
from stlab.devices.FieldfoxPNA import FieldfoxPNA as pnaclass #Import device driver for your desired PNA
import numpy as np

prefix = 'M2' #prefix for measurement folder name.  Can be anything or empty
idstring = 'Dev1_powersweep' #Additional info included in measurement folder name.  Can be anything or empty

pna = pnaclass(addr='TCPIP::192.168.1.151::INSTR',reset=True,verb=True) #Initialize device communication and reset

pna.SetRange(4e9,8e9) #Set frequency range in Hz
pna.SetIFBW(300.) #Set IF bandwidth in Hz
pna.SetPoints(1001) #Set number of frequency points

powstart = -45.
powstop = -0.
steps = 5
powers = np.linspace(powstart,powstop,steps) #generate power sweep steps

for i,rfpower in enumerate(powers):
    pna.SetPower(rfpower) #set pna power
    data = pna.Measure2ports() #Trigger 2 port measurement and retrieve data in Re,Im format.  Returns OrderedDict
    #Add Columns for S parameters in dB
    S11dB = 20.*np.log10( [ np.sqrt(np.power(a,2.)+np.power(b,2.)) for a,b in zip(data['S11re ()'],data['S11im ()']) ] )
    S21dB = 20.*np.log10( [ np.sqrt(np.power(a,2.)+np.power(b,2.)) for a,b in zip(data['S21re ()'],data['S21im ()']) ] )
    npoints = len(data['Frequency (Hz)'])
    data['Power (dBm)'] = np.full(npoints,rfpower)
    data['S11dB (dB)'] = S11dB
    data['S21dB (dB)'] = S21dB
    if i==0: #if on first measurement, create new measurement file and folder using titles extracted from measurement
        myfile,fullfilename,_ = stlab.newfile(prefix,idstring,data.keys())
    stlab.savedict(myfile, data) #Save measured data to file.  Written as a block for spyview.
    #Create metafile for spyview at each measurement step
    stlab.metagen.fromarrays(fullfilename,data['Frequency (Hz)'],powers[0:i+1],xtitle='Frequency (Hz)',ytitle='Power (dB)',colnames=data.keys())
myfile.close() #Close file

