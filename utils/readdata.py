# Read data from measurement file
# File has a certain number of columns and multiple measurement sets
# Sets are separated by a newline
# Single title line and ', ' field delimeter

import numpy as np
from collections import OrderedDict

def readdat(filename):
    with open(filename,'r') as f:
        variables = {}
        ivar = 0
        mylists = {}
        col = []
        currentvarname =""

        line = f.readline()
        line = line.strip("\n").strip("# ")
        print(line)
        names = line.split(', ')
        print(names)

        block =[]
        arrayofdicts = []
        for point in f:
            if point == '\n':
                block = np.asarray(block)
                block = block.T
                newdict=OrderedDict()
                for name,dat in zip(names,block):
                    newdict[name] = dat
                arrayofdicts.append(newdict)
                block = []
                continue
            point = [ float(x) for x in point.strip('\n').split(', ')]
            block.append(point)
        block = np.asarray(block)
        block = block.T
        newdict=OrderedDict()
        for name,dat in zip(names,block):
            newdict[name] = dat
        arrayofdicts.append(newdict)
        return arrayofdicts

def reads2p(filename):
    with open(filename,'r') as f:
        names = ['Frequency (Hz)', 'S11re ()', 'S11im ()', 'S21re ()', 'S21im ()', 'S12re ()', 'S12im ()', 'S22re ()', 'S22im ()']

        measurement = []
        for line in f:
            if line.startswith('!') or line.startswith('#'):
                continue
            line = [ float(x) for x in line.strip('\n').split()]
            measurement.append(line)
        measurement = np.asarray(measurement)
        measurement = measurement.T
        mydict=OrderedDict()
        for name,data in zip(names,measurement):
            mydict[name]=data
        return mydict

# Imports a QUCS formatted data file.  The data is returned as a dict 
# containing np.array's for each variable with the QUCS variable name
# as dict key.  Complex values are conserved.

pi = np.pi

def readQUCS(filename):
    with open(filename,'r') as f:
        variables = {}
        ivar = 0
        mylists = {}
        col = []
        currentvarname =""

        for line in f:
            varfound = line.find('<')
            varendfound = line.find('/')
            if varendfound != -1:
                mylists[currentvarname] = np.array(col)
                col = []
            elif varfound != -1:
                line = line.strip("\n").strip(">").strip("<")
                words = line.split()
                vartype = words[0]
                varname = words[1]
                print(vartype, varname)
                if vartype == 'Qucs':
                    continue
                elif vartype == 'indep' or vartype=='dep':
                    currentvarname = varname
            elif varfound == -1:
                if 'j' not in line:
                    col.append(float(line))
                else:
                    ij = line.find('j')
                    x = float(line[0:ij-1])
                    y = float(line[ij-1:].replace("j",""))
                    col.append( complex(x,y) )
        return mylists
