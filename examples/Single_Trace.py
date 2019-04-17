"""Example script to retrieve a single trace from a PNA

Does not reset PNA.  The idea is that the user sets up the trace on screen and then
runs this script to retrieve it.

"""

import stlab
import numpy as np

prefix = 'M'  #prefix for measurement folder name.  Can be anything or empty
idstring = 'He7_2_to_1_TR_tru'  #Additional info included in measurement folder name.  Can be anything or empty

pna = stlab.adi(
    addr='TCPIP::192.168.1.93::INSTR', reset=False,
    verb=True)  #Initialize device communication and reset

data = pna.MeasureScreen_pd(
)  #Trigger 2 port measurement and retrieve data in Re,Im format.  Returns OrderedDict
myfile = stlab.newfile(prefix, idstring, autoindex=True)
stlab.saveframe(
    myfile,
    data)  #Save measured data to file.  Written as a block for spyview.
#Create metafile for spyview at each measurement step
stlab.metagen.fromarrays(
    myfile,
    data['Frequency (Hz)'], [0],
    xtitle='Frequency (Hz)',
    ytitle='None',
    colnames=list(data))
myfile.close()  #Close file
