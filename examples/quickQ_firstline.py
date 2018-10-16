"""Example for quick measurement and fit of a Q factor using stlab.S11fit

Takes a user defined label as command line argument to name the output files (one figure, one complex trace and the fit parameters)

"""

import stlab #fitting routines imported here.  Callable as stlab.S11fit(...) and stlab.S11func(...)
import numpy as np
#from stlab.devices.RS_ZND import RS_ZND_pna as pnaclass #Import device driver for PNA
from matplotlib import pyplot as plt #import graphing library
import sys
import re
import os


tag = sys.argv[1]
data = stlab.readdata.readdat_pd(tag,nlines=10)
data = data[0]

try:
    measpow = data['Power (dBm)'][0] #retrieve power for plot
except KeyError:
    measpow = 'NA'
print(data.keys()) #Show available data columns on screen

x = data['Frequency (Hz)'] #Get frequency array from measurement
#Regular expression to find correct label for fitting columns.  Will assing SXX into sparam for first found S parameter trace in measurement
pattern = '^S\d{2}(re|im)'
pattern = re.compile(pattern)
for lab in data.keys():
    if  pattern.match(lab):
        sparam = lab[:3]
        break

#************************************************
fitwidth = 5. #Width of trace to fit in units of detected peak width
trimwidth = 3. #Width to trim around detected peak for background fit in units of detected peak width
ftype = 'A' # A and -A are reflection models while B and -B are side coupled models
doplots = True #Show debugging plots
margin = 51 #smoothing margin for peak detection
#************************************************


#*************************** DO FIT AND RETURN RESULT *********************************************************
z = np.asarray([a+1j*b for a,b in zip(data[sparam + 're ()'],data[sparam + 'im ()'])]) #Convert S parameter data from Re,Im to complex array
params,x0,z0,stats = stlab.S11fit(x,z,ftype=ftype,doplots=doplots,trimwidth=trimwidth,fitwidth=fitwidth,margin=margin) #Do fit with some given parameters.  More options available.
zfit = stlab.S11func(x0,params,ftype=ftype)
#***************************************************************************************************************

#Make a plot of the fit result (magnitude only)
fig = plt.figure()
plt.plot(x,20.*np.log10(np.abs(z)))
plt.plot(x0,20.*np.log10(np.abs(zfit)))
plt.xlabel('Frequency (Hz)')
plt.ylabel(sparam +' (dB)')
newstr = ''
for q in params:
    if params[q].name in ['Qint','Qext','f0','theta']:
        newstr+="{} = {} \n     +- {}\n".format(params[q].name,params[q].value,params[q].stderr)
Ql = 1/(1/params['Qint'].value+1/params['Qext'].value)
newstr+='Qloaded = {}\n'.format(Ql)        
newstr+='RFpow = '+str(measpow)+' dBm'
ax1 = plt.gca()
plt.text(0.55,0.15,newstr,fontsize=7,transform=ax1.transAxes)



try:
    tag = sys.argv[1]
    tag = os.path.splitext(os.path.basename(tag))[0]
except IndexError:
    tag = ''

#Save fitted trace using tag
prefix = 'quickQ'
idstring = tag
print(idstring,prefix)
myfile = stlab.newfile(prefix,idstring,data.keys(),usedate=False,usefolder=True,autoindex=True)
outfilename = os.path.splitext(myfile.name)[0]
stlab.saveframe(myfile,data)
myfile.close()


#Save figure
fig.savefig(outfilename + '.plot.png')
plt.show()

#Save fit parameters
myfile = open(outfilename + '.fit.dat','w')
for q in params:
    myfile.write("{} = {} +- {}\n".format(params[q].name,params[q].value,params[q].stderr) )
myfile.close()


