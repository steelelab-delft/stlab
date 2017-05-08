#Example for quick measurement and fit of a Q factor using stlab.S11fit.
#Takes a user defined label as command line argument to name the output files (one figure, one complex trace and the fit parameters)
import stlab #fitting routines imported here.  Callable as stlab.S11fit(...) and stlab.S11func(...)
import numpy as np
#from stlab.devices.RS_ZND import RS_ZND_pna as pnaclass #Import device driver for PNA
from stlab.devices.PNAN5221A import PNAN5221A as pnaclass #Import device driver for PNA
from matplotlib import pyplot as plt #import graphing library
import sys

try:
    tag = sys.argv[1]
except IndexError:
    tag = ''

pna = pnaclass(reset=False,verb=True) #Initialize device but do not reset.
pna.SetContinuous(False)
#'addr' is the VISA address string for the device
#Since reset is set to False, this script assumes that the sweep settings are already set before starting
#These could of course be set through member methods of the pna.  See driver for options.
data = pna.MeasureScreen() #Set 2 port measurement, trigger measurement and retrieve data.  Data is returned as an OrderedDict
# If calibration is used, both calibrated and uncalibrated data is returned
print(data.keys()) #Show available data columns on screen

x = data['Frequency (Hz)'] #Get frequency array from measurement
z = np.asarray([a+1j*b for a,b in zip(data['S21re ()'],data['S21im ()'])]) #Convert S parameter data from Re,Im to complex array
fitwidth = 5.
if fitwidth == None:
    params = stlab.S11fit(x,z,doplots=False,trimwidth=3.,fitwidth=fitwidth) #Do fit with some standard parameters.  More options available.
    x0 = x
else:
    params,x0,z0 = stlab.S11fit(x,z,doplots=True,trimwidth=3.,fitwidth=fitwidth) #Do fit with some standard parameters.  More options available.
print(type(params))
#Make a plot of the fit result (magnitude only)
zfit = stlab.S11func(x0,params)
fig = plt.figure()
plt.plot(x,20.*np.log10(np.abs(z)))
plt.plot(x0,20.*np.log10(np.abs(zfit)))
plt.xlabel('Frequency (Hz)')
plt.ylabel('S21 (dB)')
plt.show()
fig.savefig('quickQ' + tag + '.png')

myfile = open('quickQ' + tag + '.fit.dat','w')
for q in params:
    myfile.write(params[q].name + " = %.7e +- %.7e" % (params[q].value,params[q].stderr) + '\n')

myfile = open('quickQ' + tag +'.trace.dat','w')
for a,b,c in zip(x, np.real(z), np.imag(z)):
    a = str(a)
    b = str(b)
    c = str(c)
    myfile.write(', '.join([a,b,c]) + '\n')
