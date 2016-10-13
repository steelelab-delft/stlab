#Example for quick measurement and fit of a Q factor using stlab.S11fit.  No data is saved.
import stlab #fitting routines imported here.  Callable as stlab.S11fit(...) and stlab.S11func(...)
import numpy as np
from stlab.devices.RS_ZND import RS_ZND_pna #Import device driver for RS ZND
from matplotlib import pyplot as plt #import graphing library

pna = RS_ZND_pna(addr='TCPIP::192.168.1.149::INSTR',reset=False,verb=True) #Initialize device but do not reset.
#'addr' is the VISA address string for the device
#Since reset is set to False, this script assumes that the sweep settings are already set before starting
#These could of course be set through member methods of the pna.  See driver for options.
data = pna.Measure2ports() #Set 2 port measurement, trigger measurement and retrieve data.  Data is returned as an OrderedDict
# If calibration is used, both calibrated and uncalibrated data is returned
print(data.keys()) #Show available data columns on screen

x = data['Frequency (Hz)'] #Get frequency array from measurement
z = np.asarray([a+1j*b for a,b in zip(data['S21re unc ()'],data['S21im unc ()'])]) #Convert S parameter data from Re,Im to complex array
params = stlab.S11fit(x,z,doplots=False,trimwidth=3.) #Do fit with some standard parameters.  More options available.

#Make a plot of the fit result (magnitude only)
zfit = stlab.S11func(x,params)
fig = plt.figure()
plt.plot(x,20.*np.log10(np.abs(z)))
plt.plot(x,20.*np.log10(np.abs(zfit)))
plt.show()

