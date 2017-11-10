from collections import OrderedDict
import numpy as np
from scipy import ndimage
import pickle
import struct


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

def checkEqual1(iterator): #Returns True if all elements in iterator are equal or is empty
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

def dictarr_to_mtx(data, key, rangex=None, rangey=None, xkey=None, ykey=None, xtitle=None, ytitle=None, ztitle = None):
#data is an array of dict-like (dict, OrderedDict, stlabdict), key is the z data (matrix values) column.
#if xkey/ykey is provided, this column is used as the x/y range values.  These values are also used as x/y titles.  x is made to run across matrix columns and y across lines.
#This means that if x is the "slow" variable in the measurement file, the output matrix will be transposed relative to the default behavior.
#if rangex/rangey are provided, these override the xkey/ykey assignment.  Should be array-like with the correct lengths.
#if xtitle/ytitle are provided, these override the xkey/ykey title assignment.
#If neither ranges, titles or keys are provided, defaults are given.  The z column for each set in the data array will be placed as a line in the output matrix (default behavior)
#Script assumes that ranges are not changing from set to set in data.  Ranges can however be non linear.

    #Build initial matrix.  Appends each data column as line in zz    
    zz = [];
    for line in data:
        zz.append(line[key])
    #convert to np matrix
    zz = np.asmatrix(zz)
    if not ztitle:
        ztitle = key

    #No keys or ranges given:
    if rangex==None and rangey==None and xkey==None and ykey==None:
        if xtitle == None:
            xtitle = 'xtitle' #Default title
        if ytitle == None:
            ytitle = 'ytitle' #Default title
        return stlabmtx(zz, xtitle=xtitle, ytitle=ytitle, ztitle=ztitle)

    #If ranges but no keys are given
    elif (xkey == None and ykey==None) and (rangex !=None and rangey != None):
        if xtitle == None:
            xtitle = 'xtitle' #Default title
        if ytitle == None:
            ytitle = 'ytitle' #Default title
        return stlabmtx(zz, rangex, rangey, xtitle, ytitle, ztitle)

    #If keys but no ranges given
    elif (xkey != None and ykey != None) and (rangex == None and rangey == None):
        #Take first dataset and extract the two relevant columns
        line = data[0]
        xx = line[xkey]
        yy = line[ykey]
        #Check which is slow (one with all equal values is slow)
        xslow,yslow = (checkEqual1(xx),checkEqual1(yy))
        #Both can not be fast or slow
        if xslow == yslow:
            print('dictarr_to_mtx: Warning, invalid xkey and ykey.  Using defaults')
            if xtitle == None:
                xtitle = 'xtitle' #Default title
            if ytitle == None:
                ytitle = 'ytitle' #Default title
            return stlabmtx(zz, xtitle=xtitle, ytitle=ytitle, ztitle=ztitle)
        #if x is slow, matrix needs to be transposed
        if xslow:
            zz = zz.T
            xx = []
            for line in data:
                xx.append(line[xkey][0])
        #Case of y slow
        #if x is slow, matrix is already correct
        if yslow:
            yy = []
            for line in data:
                yy.append(line[ykey][0])
        xx = np.asarray(xx)
        yy = np.asarray(yy)
        #Sort out titles
        titles = tuple(data[0].keys())
        if xtitle == None:
            if isinstance(xkey, str):
                xtitle = xkey #Default title
            elif isinstance(xkey, int):
                xtitle = titles[xkey]
        if ytitle == None:
            if isinstance(ykey, str):
                ytitle = ykey #Default title
            elif isinstance(ykey, int):
                ytitle = titles[ykey]
        return stlabmtx(zz, xx, yy, xtitle, ytitle, ztitle)

    #Mixed cases (one key and one range) are not implemented
    else:
        print('dictarr_to_mtx: Warning, invalid keys and ranges.  Using defaults')
        if xtitle == None:
            xtitle = 'xtitle' #Default title
        if ytitle == None:
            ytitle = 'ytitle' #Default title
        return stlabmtx(zz, xtitle=xtitle, ytitle=ytitle, ztitle=ztitle)
    return 

def sub_cbc(data, lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
    new_mtx = []
    mtx=data.copy() # for some reason this makes it faster
    for y in mtx:
        # Find boundaries
        min0 = max(y.min(),low_limit)
        max0 = min(y.max(),high_limit)
        crop = np.logical_and(min0<=y,y<=max0) # crop list accordingly
        # Find upper and lower percentiles and assign truthvalue to elements
        # This is a major time contributor
        low_thres = np.percentile(y[crop],lowp)
        high_thres = np.percentile(y[crop],100-highp)
        crop2 = np.logical_and(low_thres<=y,y<=high_thres) # crop again
        mean = y[crop2].mean() # Calculate mean of remaining values
        new_mtx.append(y-mean)
    return np.matrix(np.squeeze(new_mtx))

def xderiv(data,rangex,direction=1,axis=1):
    dx = np.abs(rangex[0]-rangex[1])
    if direction==-1:
        dx = -dx
    z = np.squeeze(np.array(data))
    dz = np.gradient(z, dx, axis=axis)    
    return np.matrix(np.squeeze(dz))
    
# Use slow if spacing is non-uniform
def xderiv_slow(data,rangex,direction=1):
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
    def __init__(self, mtx=np.zeros([0,0]), rangex=None, rangey=None, xtitle='xtitle', ytitle='ytitle', ztitle = 'ztitle'):
        self.mtx = np.matrix(copy.deepcopy(mtx))
        print(self.mtx.shape)
        self.processlist = []
        self.pmtx = self.mtx
        if rangex is None:
            self.rangex = np.arange(self.mtx.shape[1])
        else:
            self.rangex = np.asarray(rangex)
        if rangey is None:
            self.rangey = np.arange(self.mtx.shape[0])
        else:
            self.rangey = np.asarray(rangey)
        self.xtitle=str(xtitle)
        self.ytitle=str(ytitle)
        self.ztitle = str(ztitle)
        self.xtitle0=self.xtitle
        self.ytitle0=self.ytitle
        self.ztitle0=self.ztitle
        self.rangex0 = self.rangex
        self.rangey0 = self.rangey
    def getextents(self):
        return (self.rangex[0],self.rangex[-1],self.rangey[-1],self.rangey[0])
    # Functions from spyview
    def absolute(self):
        self.pmtx = abs(self.pmtx)
        self.processlist.append('abs')
    def flip(self,x=False,y=False):
        x=bool(x)
        y=bool(y)
        if x:
            self.pmtx = np.fliplr(self.pmtx)
            self.rangex = self.rangex[::-1]
        if y:
            self.pmtx = np.flipud(self.pmtx)
            self.rangey = self.rangey[::-1]
        self.processlist.append('flip {:d},{:d}'.format(x,y))
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
        self.xtitle, self.ytitle = self.ytitle, self.xtitle
        self.rangex , self.rangey = self.rangey, self.rangex[::-1]
    def rotate_cw(self):
        # still lacking the switching of the axes
        self.pmtx = np.rot90(self.pmtx,3)
        self.processlist.append('rotate_cw')
        self.xtitle, self.ytitle = self.ytitle, self.xtitle
        self.rangex , self.rangey = self.rangey[::-1], self.rangex
    def scale_data(self,factor=1.):
        self.pmtx = factor*self.pmtx
        self.processlist.append('scale {}'.format(factor))
    def sub_cbc(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        self.pmtx = sub_cbc(self.pmtx,lowp,highp,low_limit,high_limit)
        self.processlist.append('sub_cbc {},{},{},{}'.format(lowp,highp,low_limit,high_limit))
    def sub_lbl(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        self.pmtx = sub_cbc(self.pmtx.T,lowp,highp,low_limit,high_limit).T
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
        mtx = self.pmtx.copy()
        self.pmtx = xderiv(mtx,self.rangey,direction,axis=0)
        self.processlist.append('yderiv {}'.format(direction))
    #Use slow versions for unequally spaced ranges
    def xderiv_slow(self,direction=1):
        mtx = self.pmtx.copy()
        self.pmtx = xderiv(mtx,self.rangex,direction)
        self.processlist.append('xderiv_slow {}'.format(direction))
    def yderiv_slow(self,direction=1):
        mtx = self.pmtx.copy().T
        self.pmtx = xderiv(mtx,self.rangey,direction).T
        self.processlist.append('yderiv_slow {}'.format(direction))
    
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
        self.xtitle = self.xtitle0
        self.ytitle = self.ytitle0
        self.rangex = self.rangex0
        self.rangey = self.rangey0
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

    #Uses pickle to save to file
    def save(self,name = 'output'):
        filename = name + '.mtx.pkl'
        with open(filename, 'wb') as outfile:
            pickle.dump(self,outfile, pickle.HIGHEST_PROTOCOL)
    #To load:
    #import pickle
    #with open(filename, 'rb') as input:
    #   mtx1 = pickle.load(input)

    def savemtx(self,filename = './output'):
        filename = filename + '.mtx'
        with open(filename, 'wb') as outfile:
            ztitle = self.ztitle
            xx = self.rangex
            yy = self.rangey
            line = ['Units',ztitle, self.xtitle,'{:e}'.format(xx[0]),'{:e}'.format(xx[-1]), self.ytitle,'{:e}'.format(yy[0]),'{:e}'.format(yy[-1]), 'Nothing',str(0),str(1)]
            mystr = ', '.join(line)
            mystr = bytes(mystr + '\n', 'ASCII')
            outfile.write(mystr)
            mystr = str(self.pmtx.shape[1]) + ' ' + str(self.pmtx.shape[0]) + ' ' + '1 8\n'
            mystr = bytes(mystr, 'ASCII')
            outfile.write(mystr)
            data = self.pmtx
            data = np.squeeze(np.asarray(np.ndarray.flatten(data,order='F')))
            print(len(data))
            s = struct.pack('d'*len(data), *data)
            outfile.write(s)

#           Units, Data Value ,Y, 0.000000e+00, 2.001000e+03,Z, 0.000000e+00, 6.010000e+02,Nothing, 0, 1
#           2001 601 1 8

            #Units, Dataset name, xname, xmin, xmax, yname, ymin, ymax, zname, zmin, zmax
            #nx ny nz length

            #dB, S21dB, Frequency (Hz), 6.000000e+09, 8.300000e+09, Vgate (V), 3.000000e+01, -3.000000e+01, Nothing, 0, 1
            #2001 601 1 8

    def loadmtx(self,filename):
        with open(filename,'rb') as infile:
            content = infile.readline()
            content = content.decode('ASCII')
            if content[:5] == 'Units':
                content = content.split(',')
                content = [x.strip() for x in content]
                self.ztitle0 = content[1]
                self.xtitle0 = content[2]
                self.ytitle0 = content[5]
                xlow = np.float64(content[3])
                xhigh = np.float64(content[4])
                ylow = np.float64(content[6])
                yhigh = np.float64(content[7])
                content = infile.readline()
                content = content.decode('ASCII')
                content = content.split(' ')
                nx = int(content[0])
                ny = int(content[1])
                lb = int(content[3])
                self.rangex0 = np.linspace(xlow,xhigh,nx)
                self.rangey0 = np.linspace(ylow,yhigh,ny)
            else:
                content = content.decode('ASCII')
                content = content.split(' ')
                nx = int(content[0])
                ny = int(content[1])
                lb = int(content[3])
                self.rangex0 = np.linspace(1,nx,nx)
                self.rangey0 = np.linspace(1,ny,ny)
            n = nx*ny
            content = infile.read()
            if lb == 8:
                s = struct.unpack('d'*n, content)
            elif lb == 4:
                s = struct.unpack('f'*n, content)
            s = np.asarray(s)
            s = np.matrix(np.reshape(s,(ny,nx),order='F'))
            self.mtx = s
            self.reset()
