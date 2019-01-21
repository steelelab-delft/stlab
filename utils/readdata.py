# Read data from measurement file
# File has a certain number of columns and multiple measurement sets
# Sets are separated by a newline
# Single title line and ', ' field delimeter

import numpy as np
import pandas as pd
from stlab.utils.stlabdict import stlabdict

def readdat(filename,delim=', ',nlines=None):
    return readdat_pd(filename,delim,nlines)
    '''
    with open(filename,'r') as f:
        variables = {}
        ivar = 0
        mylists = {}
        col = []
        currentvarname =""

        line = f.readline()
        line = line.strip("\n").strip("# ")
#        print(line)
        names = line.split(delim)
        print(names)

        block =[]
        arrayofdicts = []
#        arrayofframes = []
        nblocks = 0
            
        for point in f:
            if point[0] == '#':
                continue
            if point == '\n':
                block = np.asarray(block)
                block = block.T
                newdict=stlabdict()
                for name,dat in zip(names,block):
                    newdict[name] = dat
                arrayofdicts.append(newdict)
#                arrayofframes.append(pd.DataFrame(newdict))
                block = []
                nblocks += 1
                if nlines == None:
                    continue
                elif nblocks < nlines:
                    continue
                else:
                    break
            point = [ float(x) for x in point.strip('\n').split(delim)]
            block.append(point)
        if len(block) != 0:
            block = np.asarray(block)
            block = block.T
            newdict=stlabdict()
            for name,dat in zip(names,block):
                newdict[name] = dat
            arrayofdicts.append(newdict)
#            arrayofframes.append(pd.DataFrame(newdict))
#        return arrayofframes
        return arrayofdicts
    '''

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
        mydict=stlabdict()
        for name,data in zip(names,measurement):
            mydict[name]=data
        return pd.DataFrame(mydict)
#        return mydict

# Imports a QUCS formatted data file.  The data is returned as a dict 
# containing np.array's for each variable with the QUCS variable name
# as dict key.  Complex values are conserved.

pi = np.pi

def readQUCS(filename):
    with open(filename,'r') as f:
        variables = stlabdict()
        ivar = 0
        mylists = stlabdict()
        col = []
        currentvarname =""

        for line in f:
            varfound = line.find('<')
            varendfound = line.find('/')
            if varendfound != -1:
                mylists[vartype + '_' + currentvarname] = np.array(col)
                col = []
            elif varfound != -1:
                line = line.strip("\n").strip(">").strip("<")
                words = line.split()
                vartype = words[0]
                varname = words[1]
#                print("Words = ",words)
                print(vartype, varname)
                if vartype == 'Qucs':
                    continue
                elif vartype == 'indep' or vartype=='dep':
                    currentvarname = varname
                    if vartype == 'dep':
                        swept = ['indep_' + x for x in words[2:]]
                        print(swept)
            elif varfound == -1:
                if 'j' not in line:
                    col.append(float(line))
                else:
                    ij = line.find('j')
                    x = float(line[0:ij-1])
                    y = float(line[ij-1:].replace("j",""))
                    col.append( complex(x,y) )
        return mylists,swept


def readdat_pd(filename,delim=', ',nlines=None):
    with open(filename,'r') as f:
        variables = {}
        ivar = 0
        mylists = {}
        col = []
        currentvarname =""

        line = f.readline()
        line = line.strip("\n").strip("# ")
#        print(line)
        names = line.split(delim)
        print(names)

        block =[]
        arrayofframes = []
        nblocks = 0
            
        for point in f:
            if point == '\n':
                block = np.asarray(block)
                block = block.T
                newframe = pd.DataFrame()
                for name,dat in zip(names,block):
                    newframe[name] = dat
                arrayofframes.append(newframe)
                block = []
                nblocks += 1
                if nlines == None:
                    continue
                elif nblocks < nlines:
                    continue
                else:
                    break
            point = [ float(x) for x in point.strip('\n').split(delim)]
            block.append(point)
        if len(block) != 0:
            block = np.asarray(block)
            block = block.T
            newframe = pd.DataFrame()
            for name,dat in zip(names,block):
                newframe[name] = dat
            arrayofframes.append(newframe)
        return arrayofframes

def reads2p_pd(filename):
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
        myframe=pd.DataFrame()
        for name,data in zip(names,measurement):
            myframe[name]=data
        return myframe


pi = np.pi

def readQUCS_pd(filename):  #BROKEN
    with open(filename,'r') as f:
        ivar = 0
        mylists = pd.DataFrame()
        col = []
        currentvarname =""

        for line in f:
            varfound = line.find('<')
            varendfound = line.find('/')
            if varendfound != -1:
                mylists[vartype + '_' + currentvarname] = np.array(col)
                col = []
            elif varfound != -1:
                line = line.strip("\n").strip(">").strip("<")
                words = line.split()
                vartype = words[0]
                varname = words[1]
#                print("Words = ",words)
                print(vartype, varname)
                if vartype == 'Qucs':
                    continue
                elif vartype == 'indep' or vartype=='dep':
                    currentvarname = varname
                    if vartype == 'dep':
                        swept = ['indep_' + x for x in words[2:]]
                        print(swept)
            elif varfound == -1:
                if 'j' not in line:
                    col.append(float(line))
                else:
                    ij = line.find('j')
                    x = float(line[0:ij-1])
                    y = float(line[ij-1:].replace("j",""))
                    col.append( complex(x,y) )
        return mylists,swept
