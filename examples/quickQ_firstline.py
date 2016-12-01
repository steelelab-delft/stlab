#Example for quick S11fit of the first line in a large datafile
#Takes a command line argument: the filename of the datafile and outputs some results (one figure, one complex trace and the fit parameters)
import stlab #fitting routines imported here.  Callable as stlab.S11fit(...) and stlab.S11func(...)
import numpy as np
from matplotlib import pyplot as plt #import graphing library
import sys

tag = sys.argv[1]
alldata = stlab.readdata.readdat(tag)
data = alldata[0]
print(data.keys()) #Show available data columns on screen

x = data['Frequency (Hz)'] #Get frequency array from measurement
z = np.asarray([a+1j*b for a,b in zip(data['S21re ()'],data['S21im ()'])]) #Convert S parameter data from Re,Im to complex array
params = stlab.S11fit(x,z,doplots=True,trimwidth=5.,fitwidth = 20.) #Do fit with some standard parameters.  More options available.
#Make a plot of the fit result (magnitude only)
zfit = stlab.S11func(x,params)
fig = plt.figure()
plt.plot(x,20.*np.log10(np.abs(z)))
plt.plot(x,20.*np.log10(np.abs(zfit)))
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
