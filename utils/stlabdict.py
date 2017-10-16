from collections import OrderedDict
import numpy as np

class stlabdict(OrderedDict):
    def __init__(self, *args, **kwargs):
            super(stlabdict, self).__init__(*args, **kwargs)
    def addparcolumn(self,colname,colval): #adds a column to 
        keys = list(self.keys())
        x = self[keys[0]]
        n = len(x)
        self[colname] = np.full(n,colval)
        return
    def line(self,nn):
        ret = stlabdict()
        for key in self.keys():
            ret[key] = self[key][nn]
        return ret
    def __getitem__(self, key):
        if key in self.keys():
            return super(stlabdict, self).__getitem__(key)
        elif isinstance( key, int ) and key >= 0:
            return self[list(self.keys())[key]]
        else:
            raise KeyError
    def ncol(self):
        return len(self.keys())
    def nline(self):
        a = len(self[list(self.keys())[0]])
        for key in self.keys():
            if len(self[key]) is not a:
                print('Columns with different length!!?')
        return a
    def matrix(self):
        mat = []
        for key in self.keys():
            col = []
            for x in self[key]:
                col.append(x)
            mat.append(col)
        mat = np.transpose(mat)
        return mat
            

import copy
class stlabmtx():
    def __init__(self, mtx, rangex=None, rangey=None):
        self.mtx = np.matrix(copy.deepcopy(mtx))
        print(self.mtx.shape)
        self.processlist = []
        self.pmtx = self.mtx
        if rangex is None:
            self.rangex = np.arange(self.mtx.shape[1])
        else:
            self.rangex = rangex
        if rangey is None:
            self.rangey = np.arange(self.mtx.shape[0])
        else:
            self.rangey = rangey
    def offset(self,x=0):
        self.pmtx = self.pmtx + x
        self.processlist.append('offset {}'.format(x))
    def saveprocesslist(self,filename = './process.pl'):
        myfile = open(filename,'w')
        for line in self.processlist:
            myfile.write(line + '\n')
        myfile.close()
    def applystep(self,line):
            func,pars = line.split(' ')
            pars = pars.split(',')
            func = func.strip()
            if func is '':
                return
            elif func == 'offset':
                pars = [float(pars[0])]
            method = getattr(self, func)
            method(*pars)
    def applyprocesslist(self,pl):
        for line in pl:
            self.applystep(line)
    def applyprocessfile(self,filename):
        with open(filename,'r') as myfile:
            for line in myfile:
                if '#' == line[0]:
                    continue
                self.applystep(line)
    def reset(self):
        self.processlist = []
        self.pmtx = self.mtx
    def delstep(self,ii):
        newpl = copy.deepcopy(self.processlist)
        del newpl[ii]
        self.reset()
        self.applyprocesslist(newpl)
    def insertstep(self,ii,line):
        newpl = copy.deepcopy(self.processlist)
        newpl.insert(ii,line)
        self.reset()
        self.applyprocesslist(newpl)


