from collections import OrderedDict
import numpy as np
from scipy import ndimage

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

#Auxiliary processing functions for stlabmtx
def dict_to_mtx(data, key, rangex=None, rangey=None, xkey=None, ykey=None):
    xx = []; yy = []; zz = [];
    for line in data:
        zz.append(line[key])
        if xkey:
            xx.append(line[xkey])
        if ykey:
            yy.append(line[ykey])
    zz = np.asmatrix(zz)
    if (rangex and xkey) or (rangey and ykey):
        raise KeyError
    if xkey:
        xx = np.asarray(xx)
        rangex = np.linspace(xx[0][0],xx[-1][-1],zz.shape[0])
    if ykey:
        yy = np.asarray(yy)
        rangey = np.linspace(yy[0][0],yy[-1][-1],zz.shape[1])
    return stlabmtx(zz, rangex=rangex, rangey=rangey)

def sub_cbc(data, lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
    mtx = data
    for i in range(mtx.shape[1]):
        y = mtx[:,i]
        # Find boundaries
        min0 = max(y.min(),low_limit)
        max0 = min(y.max(),high_limit)
        # crop list accordingly
        idx_crop = [i for i,val in enumerate(y) if min0<=val<=max0]
        # Find upper and lower percentiles and assign truthvalue to elements
        if idx_crop:
            # Might be more efficient if manually sorting once. Don't really know what np.percentile does
            low_thres = np.percentile(y[idx_crop],lowp)
            high_thres = np.percentile(y[idx_crop],100-highp)
            idx = [i for i,val in enumerate(y) if low_thres<=val<=high_thres]
            # Calculate mean of remaining values
            if idx:
                mean = y[idx].mean()
                # Subtract mean from all values
                y-=mean
            mtx[:,i]=y
    return mtx   
    
def xderiv(data,rangex,direction=1):
    mtx = data
    new_mtx = []
    if direction==-1:
        x = rangex[::-1]
    else:
        x = rangex
    for line in data:
        z = np.squeeze(np.array(line))
        dz = np.zeros(x.shape,np.float)
        dz[0:-1] = np.diff(z)/np.diff(x)
        dz[-1] = (z[-1] - z[-2])/(x[-1] - x[-2])
        new_mtx.append(dz)
    return np.matrix(new_mtx)
    
#Main stlabmtx class
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
    
    # Functions from spyview
    def absolute(self):
        self.pmtx = abs(self.pmtx)
        self.processlist.append('abs')
    def flip(self,x=0,y=0):
        if bool(x):
            self.pmtx = np.fliplr(self.pmtx)
        if bool(y):
            self.pmtx = np.flipud(self.pmtx)
        self.processlist.append('flip {},{}'.format(x,y))
    def log10(self):
        self.pmtx = np.log10(self.pmtx)
        self.processlist.append('log10')
    def neg(self):
        self.pmtx = -self.pmtx
        self.processlist.append('neg')
    def offset(self,x=0):
        self.pmtx = self.pmtx + x
        self.processlist.append('offset {}'.format(x))
    def offset_axes(self,x=0,y=0):
        self.rangex+=x
        self.rangey+=y
        self.processlist.append('offset_axes {},{}'.format(x,y))
    def outlier(self,line,vertical=1):
        self.pmtx = np.delete(self.pmtx,line,axis=int(vertical))
        if bool(vertical):
            self.rangex = np.delete(self.rangex, line)
        else:
            self.rangey = np.delete(self.rangey, line)
        self.processlist.append('outlier {},{}'.format(line,vertical))
    def pixel_avg(self,nx=0,ny=0,center=0):
        nx=int(nx); ny=int(ny)
        if bool(center):
            self.pmtx = ndimage.generic_filter(self.pmtx, np.nanmean, size=(nx,ny), mode='constant',cval=np.NaN)
        else:
            mask = np.ones((nx, ny))
            mask[int(nx/2), int(ny/2)] = 0
            self.pmtx = ndimage.generic_filter(self.pmtx, np.nanmean, footprint=mask, mode='constant', cval=np.NaN)
        self.processlist.append('pixel_avg {},{},{}'.format(nx,ny,center))
    def rotate_ccw(self):
        # still lacking the switching of the axes
        self.pmtx = np.rot90(self.pmtx)
        self.processlist.append('rotate_ccw')
    def rotate_cw(self):
        # still lacking the switching of the axes
        self.pmtx = np.rot90(self.pmtx,3)
        self.processlist.append('rotate_cw')
    def scale_data(self,factor=1.):
        self.pmtx = factor*self.pmtx
        self.processlist.append('scale {}'.format(factor))
    def sub_cbc(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        mtx = self.pmtx.copy()
        self.pmtx = sub_cbc(mtx,lowp,highp,low_limit,high_limit)
        self.processlist.append('sub_cbc {},{},{},{}'.format(lowp,highp,low_limit,high_limit))
    def sub_lbl(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        mtx = self.pmtx.copy().T
        self.pmtx = sub_cbc(mtx,lowp,highp,low_limit,high_limit).T
        self.processlist.append('sub_lbl {},{},{},{}'.format(lowp,highp,low_limit,high_limit))
    def sub_linecut(self, pos, horizontal=1):
        pos = int(pos)
        if bool(horizontal):
            v = self.pmtx[pos,:]
            self.pmtx-=v
        else:
            v = self.pmtx[:,pos].T
            mtx = self.pmtx.T - v
            self.pmtx = mtx.T
        self.processlist.append('sub_linecut {},{}'.format(pos,horizontal))
    def xderiv(self,direction=1):
        mtx = self.pmtx.copy()
        self.pmtx = xderiv(mtx,self.rangex,direction)
        self.processlist.append('xderiv {}'.format(direction))
    def yderiv(self,direction=1):
        mtx = self.pmtx.copy().T
        self.pmtx = xderiv(mtx,self.rangey,direction).T
        self.processlist.append('yderiv {}'.format(direction))
    
    # Processlist
    def saveprocesslist(self,filename = './process.pl'):
        myfile = open(filename,'w')
        for line in self.processlist:
            myfile.write(line + '\n')
        myfile.close()
    def applystep(self,line):
            sline = line.split(' ')
            if len(sline) == 1:
                func = sline[0]
                pars = []
            else:
                pars = sline[1].split(',')
                func = sline[0].strip()
            if func is '':
                return
            else:
                pars = [float(x) for x in pars]
            method = getattr(self, func)
            print(func,pars)
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


