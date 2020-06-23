"""Two tone measurement using PNA and SMB microwave source sweeping SMB power.

Two tone measurement using PNA and SMB microwave source sweeping SMB power.

"""

import stlab
import numpy as np

prefix = '3DCu_Cavity_'  #prefix for measurement folder name.  Can be anything or empty
idstring = 'TT_Pow_Dep_3DCu_Cavity'  #Additional info included in measurement folder name.  Can be anything or empty

mypna = stlab.adi(addr='TCPIP::192.168.1.50::INSTR')  #initialize pna
mysg = stlab.adi(addr='TCPIP::192.168.1.50::INSTR')  #initialize SMB

sgpow = np.arange(-30., 18.1, 1.)  #in dBm (list of powers to sweep)
sgf0 = 3.75e9  # Hz

ifbw = 100  #in Hertz
f0 = 3.75e9  # Hz
span = 10e7  # Hz
npoints = 4001
power = -20  # dBm

#Setup PNA sweep parameters
mypna.SetIFBW(ifbw)
mypna.SetCenterSpan(f0, span)
mypna.SetPoints(npoints)
mypna.SetPower(power)

#Setup SMB frequency
mysg.setCWfrequency(sgf0)
#mypna.write('ROSC:SOUR EXT')

for i, P in enumerate(sgpow):  #Loop over desired SMB powers
    mysg.setCWpower(P)  #Set the power to current loop value
    mysg.RFon()  #Activate RF power on SMB
    data = mypna.Measure2ports()  #Execute PNA sweep and return data
    data['Power (dBm)'] = np.full(npoints, power - 20.)
    #Add some data columns to measured data
    data['SMBPower (dBm)'] = np.full(npoints, P)
    data['S11dB (dB)'] = 20. * np.log10([
        np.sqrt(np.power(a, 2.) + np.power(b, 2.))
        for a, b in zip(data['S11re ()'], data['S11im ()'])
    ])
    data['S21dB (dB)'] = 20. * np.log10([
        np.sqrt(np.power(a, 2.) + np.power(b, 2.))
        for a, b in zip(data['S21re ()'], data['S21im ()'])
    ])
    if i == 0:  #if on first measurement, create new measurement file and folder using titles extracted from measurement
        myfile = stlab.newfile(prefix, idstring, data.keys())
    stlab.savedict(
        myfile,
        data)  #Save measured data to file.  Written as a block for spyview.
    #Create metafile for spyview at each measurement step
    stlab.metagen.fromarrays(
        myfile,
        data['Frequency (Hz)'],
        sgpow[0:i + 1],
        xtitle='Frequency (Hz)',
        ytitle='SMBPower (dB)',
        colnames=data.keys())
myfile.close()
