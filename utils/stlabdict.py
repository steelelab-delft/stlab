"""Module providing data structures for data collection and analysis

The main features provided in this module are the stlabmtx class and the stlabdict class as
well as the framearr_to_mtx function.

"""


from collections import OrderedDict
import numpy as np
from scipy import ndimage
import pickle
import struct
import scipy
from scipy.ndimage.filters import gaussian_filter
import pandas as pd
from scipy.interpolate import interp1d


class stlabdict(OrderedDict):
    """Class to hold a data table with multiple lines and columns

    This class is DEPRECATED in favor of pandas DataFrame.  They serve the same
    function as an stlabdict but have much more functionality (and documentation...).

    This class is essentialy an ordered_dict (is a child of) with a few 
    convenience methods included.  Each element of the dict has an index that 
    labels the column and contains an array of numbers with the column data.
    It is basically a matrix where the column index are string constants instead
    of numbers (to more explicitly keep track or what each column contains).
    Can also be indexed by column number.

    """

    def __init__(self, *args, **kwargs):
        """Init method for stlabdict

        Simply calls the ordered_dict constructor

        """
        super(stlabdict, self).__init__(*args, **kwargs)
    def addparcolumn(self,colname,colval): #adds a column to 
        """Adds a parameter column

        A parameter column is typically a column with a constant value for all lines (i.e. power in a vna trace).
        Simply repeats the same value in an array of the same length as the other columns.  Does not work
        if there are no existing columns.

        Parameters
        ----------
        colname : str
            Column title for the new parameter column
        colval : float
            Value to fill the parameter column

        """
        keys = list(self.keys())
        x = self[keys[0]]
        n = len(x)
        self[colname] = np.full(n,colval)
        return
    def line(self,nn):
        """Gets a line from the table

        Takes a line from the stlabdict given by index.  While getting a column can be done by 
        simply taking mystlabdict[myindex], getting a line requires iterating over the dict and
        pulling out the desired line.

        Parameters
        ----------
        nn : int
            Line number to be extracted

        Returns
        -------
        ret : stlabdict
            New stlabdict with only the desired line (each element is labelled by the same column
            name as before but only contains a single float in each).        
        
        """
        ret = stlabdict()
        for key in self.keys():
            ret[key] = self[key][nn]
        return ret
    def __getitem__(self, key):
        """Overloaded indexing of the dict

        Reimplements the getting of items from the dict to allow for indexing by column position as well
        as by label

        Parameters
        ----------
        key : str or int
            Desired column index or position.  If a int is given, the method first checks if it is already an
            index.  If it is not, it returns the column given by the index position.

        """
        if key in self.keys():
            return super(stlabdict, self).__getitem__(key)
        elif isinstance( key, int ) and key >= 0:
            return self[list(self.keys())[key]]
        else:
            raise KeyError
    def ncol(self):
        """Get the number of columns
    
        Returns
        -------
        int
            Number of columnms in stlabdict

        """

        return len(self.keys())
    def nline(self):
        """Get the number of lines in dict

        Checks that all columns have the same number of lines
    
        Returns
        -------
        int
            Number of lines in first column (should be the same for any column)

        """
        a = len(self[list(self.keys())[0]])
        for key in self.keys():
            if len(self[key]) is not a:
                print('Columns with different length!!?')
        return a
    def matrix(self):
        """Converts entire table into a numpy matrix.

        Returns
        -------
        numpy.matrix
            Matrix containing the same data as the stlabdict.  Loses column titles.
        """
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

def checkEqual1(iterator):
    """Check if all elements in iterator are equal or is empty

    Returns
    -------
    bool
        True if iterator empty or has the same value for all elements.  False otherwise.
    """
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

def dictarr_to_mtx(data, key, rangex=None, rangey=None, xkey=None, ykey=None, xtitle=None, ytitle=None, ztitle = None):
    """Converts an array of dicts (or stlabdicts) to an stlabmtx object

    Takes an array of dict-like (dict, OrderedDict, stlabdict), typically from a measurement file, and selects the appropriate columns for
    conversion into an stlabmtx that allows spyview like operations and processing.
    
    If neither ranges or titles are given, some defaults are filled in.  The chosen data column from each data array element will be placed
    as a line in the final matrix sequentially.

    Parameters
    ----------
    data : array of dict
        Input array of data dicts.  The dicts are expected to contain a series of arrays of floats with the same length.
    key : str
        Index of the appropriate column of each dict for the data axis of the final matrix (data values for each pixel)
    xkey, ykey : str or None, optional
        Columns to use to calculate the desired x and y ranges for the final matrix.  If these are proviced they are also
        used as the x and y titles.  x runs across the matrix columns and y along the rows.  This means that if x is the "slow" variable 
        in the measurement file, the output matrix will be transposed to accomodate this.  The ranges are assumed to be the same for all lines.
    rangex, rangey : array of float or None, optional
        If provided, they override the xkey and ykey assingnment.  They should contain arrays of the correct length for use
        on the axes.  These ranges will be saved along with the data (can be unevenly spaced).  The ranges are assumed to be the same for all lines.
    xtitle, ytitle, ztitle : str or None, optional
        Titles for the x, y and z axes.  If provided, they override the titles provided in xkey, ykey and key.

    Returns
    -------
    stlabmtx
        Resulting stlabmtx.

    """
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
        #if y is slow, matrix is already correct
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

def sub_lbl(data, lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
    new_mtx = []
    mtx=data.copy() # for some reason this makes it faster
    for y in mtx:
        # Find boundaries
        min0 = max(y.min(),low_limit)
        max0 = min(y.max(),high_limit)
        crop = np.logical_and(min0<=y,y<=max0) # crop list accordingly
        # Find upper and lower percentiles and assign truthvalue to elements
        # This is a major time contributor
        if len(y[crop]) == 0:
            print('sub_lbl: Warning, no values to average')
            mean = 0
        else:
            low_thres = np.percentile(y[crop],lowp)
            high_thres = np.percentile(y[crop],100-highp)
            crop2 = np.logical_and(low_thres<=y,y<=high_thres) # crop again
            if len(y[crop2]) == 0:
                print('sub_lbl: Warning, no values to average')
                mean = 0
            else:
                mean = y[crop2].mean() # Calculate mean of remaining values
        new_mtx.append(y-mean)
    return np.matrix(np.squeeze(new_mtx))

#Main stlabmtx_pd class
class stlabmtx():
    """stlabmtx class for spyview-like operations

    This class implements a matrix in the form of a pandas DataFrame and contains
    methods analogous to those present in spyview.

    Attributes
    ----------
    mtx : pandas.DataFrame
        Original dataframe before any processing.  The dataframe indexes are considered
        the x and y ranges on the final matrix
    pmtx : pandas.DataFrame
        Processed dataframe (filters applied)
    processlist : array of str
        List strings specifying the applied filters (in order)
    xtitle, ytitle, ztitle : str
        Titles for the x,y and z (data) axes 
    xtitle0, ytitle0, ztitle0 : str
        Initial Titles for the x,y and z (data) axes (so, in case they are changed, reset can recover them)

    """
    def __init__(self, mtx, xtitle='xtitle', ytitle='ytitle', ztitle = 'ztitle'):
        """stlab mtx initialization

        Takes an input DataFrame and sets up the object
    
        Parameters
        ----------
        mtx : pandas.DataFrame
            Intup Dataframe
        xtitle, ytitle, ztitle : str
            Title for x,y and z axes

        """
        self.mtx = copy.deepcopy(mtx)
        self.mtx.index.name = str(ytitle)
        self.mtx.columns.name = str(xtitle)
        print(self.mtx.shape)
        self.processlist = []
        self.pmtx = self.mtx
        self.xtitle=str(xtitle)
        self.ytitle=str(ytitle)
        self.ztitle = str(ztitle)
        self.xtitle0=self.xtitle
        self.ytitle0=self.ytitle
        self.ztitle0=self.ztitle
    def getextents(self):
        """Get the extents of the matrix

        Returns a tuple containing (xmin, xmax, ymin, ymax) from the axis ranges,
        typically to correctly scale the axes when plotting with matplotlib.pyplot.imshow

        Returns
        -------
        tuple of float
            Four element tuple containing (xmin,xmax,ymin,ymax)        

        """
        xs = list(self.pmtx.columns)
        ys = list(self.pmtx.index)
        return (xs[0],xs[-1],ys[-1],ys[0])
    # Functions from spyview
    def absolute(self):
        """Absolute value filter

        Applies np.abs to all elements of the matrix.  Process string :code:`abs`.

        """
        self.pmtx = np.abs(self.pmtx)
        self.processlist.append('abs')
    def crop(data,left=None,right=None,up=None,low=None):
        """Crop filter

        Crops data matrix to the given extents.  Process string :code:`crop left,right,up,low`

        Parameters
        ----------
        left : int or None, optional
            New first column of cropped array.  If None, is assumed to be the first column of the whole set (no crop)
        right : int or None, optional
            New last column of cropped array.  If None, is assumed to be the last column of the whole set (no crop).
            When given a value, the actual index specified is not included in the crop
        up : int or None, optional
            New first row of the cropped array.  If None, is assumed to be the first line of the whole set (no crop)
            When given a value, the actual index specified is not included in the crop
        low : int or None, optional
            New first row of the cropped array.  If None, is assumed to be the last line of the whole set (no crop)

        """
        #TODO check
        valdict={'left':left,'right':right,'up':up,'low':low}
        for key,val in valdict.items():
            if val==0:
                valdict[key] = None
            else:
                valdict[key] = int(val)
        data.pmtx = data.pmtx.iloc[valdict['left']:valdict['right'],valdict['up']:valdict['low']]
        for key,val in valdict.items():
            if val==None:
                valdict[key] = 0
        data.processlist.append('crop {},{},{},{}'.format(valdict['left'],valdict['right'],valdict['up'],valdict['low']))
    def flip(self,x=False,y=False):
        """Flip filter

        Reverses x and/or y axis.  Process string :code:`flip x,y` (0 is false, 1 is true).

        Parameters
        ----------
        x, y : bool, optional
            If True, x or y is flipped
    
        """
        
        x=bool(x)
        y=bool(y)
        if x:
            self.pmtx = self.pmtx.iloc[:,::-1]
        if y:
            self.pmtx = self.pmtx.iloc[::-1,:]
        self.processlist.append('flip {:d},{:d}'.format(x,y))
    def log10(self):
        """Log10 filter

        Applies np.log10 to all elements in the matrix.  Process string :code:`log10`

        """
        self.pmtx = np.log10(self.pmtx)
        self.processlist.append('log10')
    def lowpass(self,x=0,y=0):
        """Low Pass filter

        Applies a gaussian filter to the data with given pixel widths.  Other filters are yet to be implemented.
        Process string :code:`lowpass x,y`

        Parameters
        ----------
        x,y : int, optional
            Width of the filter in the x and y direction

        """
        # TODO implement different filter types
        self.pmtx.loc[:,:] = gaussian_filter( self.pmtx, sigma=[int(y),int(x)])
        self.processlist.append('lowpass {},{}'.format(x,y))
    def neg(self):
        """Negative filter

        Multiplies matrix by -1.  Process string :code:`neg`

        """
        self.pmtx = -self.pmtx
        self.processlist.append('neg')
    def offset(self,x=0):
        """Offset filter

        Offsets data values by adding given value.  Process string :code:`offset x`

        Parameters
        ----------
        x : float, optional
            Value to add to all data values

        """
        self.pmtx = self.pmtx + x
        self.processlist.append('offset {}'.format(x))
    def offset_axes(self,x=0,y=0):
        """Axes offset filter

        Offset axis values.  Process string :code:`offset_axes x,y`

        Parameters
        ----------
        x, y : float, optional
            Values to add to the axes values of the matrix

        """
        self.pmtx.columns = self.pmtx.columns + x
        self.pmtx.index = self.pmtx.index + y
        self.processlist.append('offset_axes {},{}'.format(x,y))
    def outlier(self,line,vertical=1):
        """Outlier filter
        
        Drop a line or column from the data.  Process string :code:`outlier line,vertical`

        Parameters
        ----------
        line : int
            Line or column number to drop
        vertical : {1,0}, optional
            If 1, drops a column.  If 0, drops a line

        """
        axis = 1-vertical #swap 1 and 0 since vertical axis is 0 and horizontal is 1
        self.pmtx = self.pmtx.drop(line,axis = axis)
        self.processlist.append('outlier {},{}'.format(line,vertical))
    def pixel_avg(self,nx=0,ny=0,center=0):
        """Pixel average filter
        
        Performs pixel averaging on matrix.  Process string :code:`pixel_avg nx,ny,center`

        Parameters
        ----------
        nx,ny : int, optional
            Width and height of averaging window
        center : {0,1}, optional
            I don't know what this does...
            Looks like it omits the center point of each averaging window from the average?
            
        """
        nx=int(nx); ny=int(ny)
        if bool(center):
            self.pmtx.loc[:,:] = ndimage.generic_filter(self.pmtx, np.nanmean, size=(nx,ny), mode='constant',cval=np.NaN)
        else:
            mask = np.ones((nx, ny))
            mask[int(nx/2), int(ny/2)] = 0
            self.pmtx.loc[:,:] = ndimage.generic_filter(self.pmtx, np.nanmean, footprint=mask, mode='constant', cval=np.NaN)
        self.processlist.append('pixel_avg {},{},{}'.format(nx,ny,center))
    def rotate_ccw(self):
        """Rotate counter-clockwise filter

        Rotates matrix and axes counter-clockwise.  Process string :code:`rotate_ccw`

        """
        self.ytitle, self.xtitle = self.xtitle, self.ytitle
        self.pmtx = self.pmtx.transpose()
        self.pmtx = self.pmtx.iloc[::-1,:]
        self.processlist.append('rotate_ccw')
    def rotate_cw(self):
        """Rotate clockwise filter

        Rotates matrix and axes clockwise.  Process string :code:`rotate_cw`

        """
        self.ytitle, self.xtitle = self.xtitle, self.ytitle
        self.pmtx = self.pmtx.transpose()
        self.pmtx = self.pmtx.iloc[:,::-1]
        self.processlist.append('rotate_cw')
    def scale_data(self,factor=1.):
        """Scale filter

        Scales all data by given factor.  Process string :code:`scale x`

        Parameters
        ----------
        factor : float, optional
            Value to scale the data by

        """
        self.pmtx = factor*self.pmtx
        self.processlist.append('scale {}'.format(factor))
    def sub_lbl(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        """Substract line by line filter

        The average value of each line is substracted from the data.  Parts of each line cut can be
        excluded using the high and low percentile options.  The idea is that all points are sorted in
        increasing order and a percentage from the back and front of the list is rejected for the average
        calculation.  Process string :code:`sub_lbl lowp,highp,low_limit,high_limit`

        Parameters
        ----------
        lowp : float
            Percentage of points to be rejected from the averaging on the low side.
        highp : float
            Percentage of points to be rejected from the averaging on the high side.
        low_limit : float
            Absolute value below which points are ignored for the average (and percentile calculations)
        low_limit : float
            Absolute value above which points are ignored for the average (and percentile calculations)

        """
        self.pmtx.loc[:,:] = sub_lbl(self.pmtx.values,lowp,highp,low_limit,high_limit)
        self.processlist.append('sub_lbl {},{},{},{}'.format(lowp,highp,low_limit,high_limit))
    def sub_cbc(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        """ Subtract column by column filter
    
        Same as :any:`sub_lbl` but done on a column by column basis.  Process string :code:`sub_cbc lowp,highp,low_limit,high_limit`

        """
        self.pmtx.loc[:,:] = sub_lbl(self.pmtx.values.T,lowp,highp,low_limit,high_limit).T
        self.processlist.append('sub_cbc {},{},{},{}'.format(lowp,highp,low_limit,high_limit))
    def sub_linecut(self, pos, horizontal=1):
        """Subtract lincut filter

        Selects a line or column and subtracts it from all othe lines or columns in the matrix.
        Process string :code:`sub_linecut pos,horizontal`

        Parameters
        ----------
        pos : int
            Index of line or column to be subtracted
        horizontal : {1,0}
            If 1, a line is subtrcted.  If 0 a column is subtracted

        """
        pos = int(pos)
        if bool(horizontal):
            v = self.pmtx.iloc[pos,:]
            self.pmtx = self.pmtx.subtract(v,axis=1)
        else:
            v = self.pmtx.iloc[:,pos]
            self.pmtx = self.pmtx.subtract(v,axis=0)
        self.processlist.append('sub_linecut {},{}'.format(pos,horizontal))
    def vi_to_iv(self,vmin,vmax,nbins):
        """vi to iv filter

        Reverses the data axis with the y axis of the matrix.  For example, if the data contains the voltage and the axis the current
        this filter replaces the voltage data with the corresponding current data and the axis with the voltage (I think...).
        Since the axes are expected to be ordered, this is not an immediate operation and may not be possible in many cases (repeated data values?).

        If one desires to do this with the x axis instead of the y, the matrix must first be transposed.  After the filter is applied the transpose
        can be undone.

        Process string :code:`vi_to_iv vmin,vmax,nbins`

        Parameters
        ----------
        vmin : float
            Lower end of the new y axis
        vmax : float
            Upper end of the new y axis
        nbins : int
            Number of points in the new axis

        """
        vinterpol = np.linspace(vmin,vmax,nbins)
        pmtx = [interp1d(x=self.pmtx[column],y=self.pmtx.axes[0],bounds_error=False,fill_value=np.nan)(vinterpol) for column in self.pmtx]
        self.pmtx = pd.DataFrame(np.array(pmtx).T, index=vinterpol, columns=self.pmtx.axes[1])
        self.pmtx.index.name, self.ztitle, self.xtitle = self.ztitle, self.pmtx.index.name, self.ztitle
        self.processlist.append('vi_to_iv {},{},{}'.format(vmin,vmax,nbins))
    def xderiv(self,direction=1):
        """X derivative filter

        Apply a derivative along the lines of the matrix.  Process string :code:`xderiv direction`

        Parameters
        ----------
        direction : {1,-1}
            Direction for derivative.  1 by default (normal diff derivative)
        
        """
        self.pmtx = xderiv_pd(self.pmtx,direction)
        self.processlist.append('xderiv {}'.format(direction))
    def yderiv(self,direction=1):
        """Y derivative filter

        Apply a derivative along the columns of the matrix.  Process string :code:`yderiv direction`

        Parameters
        ----------
        direction : {1,-1}
            Direction for derivative.  1 by default (normal diff derivative)
        
        """
        self.pmtx = yderiv_pd(self.pmtx,direction)
        self.processlist.append('yderiv {}'.format(direction))
    def transpose(self):
        """Transpose filter

        Transposes the data matrix (and axes).  Process string :code:`transpose`
        """
        self.ytitle, self.xtitle = self.xtitle, self.ytitle
        self.pmtx = self.pmtx.transpose()
        self.processlist.append('transpose')

    # Processlist
    def saveprocesslist(self,filename = './process.pl'):
        """Save applied filter list

        Saves the applied filters and parameters to a text file (process.pl in the current folder by default)

        Parameters
        ----------
        filename : str
            Name of the new file to save the list in.

        """
        myfile = open(filename,'w')
        for line in self.processlist:
            myfile.write(line + '\n')
        myfile.close()
    def applystep(self,line):
        """Apply step from a process list string

        Takes in input string descibing one filter application and applies it to the data

        Parameters
        ----------
        line : str
            String describing the desired filter to be applied

        """
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
        self.processlist.append(line.strip())
    def applyprocesslist(self,pl):
        """Apply all steps in array of process strings

        Takes in input list of strings descibing filters to be applied to the data and runs them.

        Parameters
        ----------
        line : str
            String describing the desired filter to be applied

        """
        for line in pl:
            self.applystep(line)
    def applyprocessfile(self,filename):
        """Apply all steps in a process list file

        Takes in input file containing a process list and applies them to the data.

        Parameters
        ----------
        filename : str
            Process file name

        """
        with open(filename,'r') as myfile:
            for line in myfile:
                if '#' == line[0]:
                    continue
                self.applystep(line)
    def reset(self):
        """Reset filters

        Resets all filters and returns matrix to its initial state

        """
        self.processlist = []
        self.xtitle = self.xtitle0
        self.ytitle = self.ytitle0
        self.pmtx = self.mtx
    def delstep(self,ii):
        """Removes a filter from the current process list by index

        Parameters
        ----------
        ii : int
            Index of filter to be removed from applied filters

        """
        newpl = copy.deepcopy(self.processlist)
        del newpl[ii]
        self.reset()
        self.applyprocesslist(newpl)
    def insertstep(self,ii,line):
        """Inserts new filter into process list

        Adds a new filter at a specific position in the process list

        Parameters
        ----------
        ii : int
            Index for the position of the new filter
        line : str
            Process string for the new filter

        """
        newpl = copy.deepcopy(self.processlist)
        newpl.insert(ii,line)
        self.reset()
        self.applyprocesslist(newpl)

    #Uses pickle to save to file
    def save(self,name = 'output'):
        """Save matrix to file

        Pickels the object and saves it to given file.

        Parameters
        ----------
        name : str
            Base filename to be used.  ".mtx.pkl" will be appended to given filename

        """
        filename = name + '.mtx.pkl'
        with open(filename, 'wb') as outfile:
            pickle.dump(self,outfile, pickle.HIGHEST_PROTOCOL)
    #To load:
    #import pickle
    #with open(filename, 'rb') as input:
    #   mtx1 = pickle.load(input)

    def savemtx(self,filename = './output'):
        """Save to Spyview mtx format

        Saves current processed matrix to a spyview mtx file

        Parameters
        ----------
        filename : str
            Name of the new mtx file.  ".mtx" will be appended.

        """
        filename = filename + '.mtx'
        with open(filename, 'wb') as outfile:
            ztitle = self.ztitle
            xx = np.array(self.pmtx.columns)
            yy = np.array(self.pmtx.index)
            line = ['Units',ztitle, self.xtitle,'{:e}'.format(xx[0]),'{:e}'.format(xx[-1]), self.ytitle,'{:e}'.format(yy[0]),'{:e}'.format(yy[-1]), 'Nothing',str(0),str(1)]
            mystr = ', '.join(line)
            mystr = bytes(mystr + '\n', 'ASCII')
            outfile.write(mystr)
            mystr = str(self.pmtx.shape[1]) + ' ' + str(self.pmtx.shape[0]) + ' ' + '1 8\n'
            mystr = bytes(mystr, 'ASCII')
            outfile.write(mystr)
            data = self.pmtx.values
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
        """Load matrix from an existing Spyview mtx file

        Parameters
        ----------
        filename : string
            Name of the mtx file to open

        """
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
                rangex0 = np.linspace(xlow,xhigh,nx)
                rangey0 = np.linspace(ylow,yhigh,ny)
            else:
                content = content.decode('ASCII')
                content = content.split(' ')
                nx = int(content[0])
                ny = int(content[1])
                lb = int(content[3])
                rangex0 = np.linspace(1,nx,nx)
                rangey0 = np.linspace(1,ny,ny)
            n = nx*ny
            content = infile.read()
            if lb == 8:
                s = struct.unpack('d'*n, content)
            elif lb == 4:
                s = struct.unpack('f'*n, content)
            s = np.asarray(s)
            s = np.matrix(np.reshape(s,(ny,nx),order='F'))
            self.mtx = pd.DataFrame(s)
            self.mtx.columns = rangex0
            self.mtx.index = rangey0
            self.reset()

stlabmtx_pd = stlabmtx


def yderiv_pd(data,direction=1):
    dy = np.diff(data.index)
    data = data.diff(axis=0,periods=direction)
    data = data.dropna(axis=0)
    if direction==-1:
        dy = -dy
    data = data.divide(dy,axis='rows')
    return data

def xderiv_pd(data,direction=1):
    return yderiv_pd(data.transpose(),direction).transpose()



def framearr_to_mtx(data, key, rangex=None, rangey=None, xkey=None, ykey=None, xtitle=None, ytitle=None, ztitle = None):
    """Converts an array of pandas DataFrame to an stlabmtx object

    Takes an array of pandas.DataFrame, typically from a measurement file, and selects the appropriate columns for
    conversion into an stlabmtx that allows spyview like operations and processing.  Is essentially the same as :any:`dictarr_to_mtx`
    but adapted for pandas DataFrame.
    
    If neither ranges or titles are given, some defaults are filled in.  The chosen data column from each data array element will be placed
    as a line in the final matrix sequentially.

    Parameters
    ----------
    data : array of dict
        Input array of frames.
    key : str
        Index of the appropriate column of each frame for the data axis of the final matrix (data values for each pixel)
    xkey, ykey : str or None, optional
        Columns to use to calculate the desired x and y ranges for the final matrix.  If these are proviced they are also
        used as the x and y titles.  x runs across the matrix columns and y along the rows.  This means that if x is the "slow" variable 
        in the measurement file, the output matrix will be transposed to accomodate this.  The ranges are assumed to be the same for all lines.
    rangex, rangey : array of float or None, optional
        If provided, they override the xkey and ykey assingnment.  They should contain arrays of the correct length for use
        on the axes.  These ranges will be saved along with the data (can be unevenly spaced).  The ranges are assumed to be the same for all lines.
    xtitle, ytitle, ztitle : str or None, optional
        Titles for the x, y and z axes.  If provided, they override the titles provided in xkey, ykey and key.

    Returns
    -------
    stlabmtx
        Resulting stlabmtx.

    """

    #Build initial matrix.  Appends each data column as line in zz    
    zz = [];
    for line in data:
        zz.append(line[key])
    #convert to np matrix
    zz = np.array(zz)
    if not ztitle:
        ztitle = str(key)

    #No keys or ranges given:
    if rangex==None and rangey==None and xkey==None and ykey==None:
        if xtitle == None:
            xtitle = 'xtitle' #Default title
        if ytitle == None:
            ytitle = 'ytitle' #Default title
        zz = pd.DataFrame(zz)
        return stlabmtx(zz, xtitle=xtitle, ytitle=ytitle, ztitle=ztitle)

    #If ranges but no keys are given
    elif (xkey == None and ykey==None) and (rangex !=None and rangey != None):
        if xtitle == None:
            xtitle = 'xtitle' #Default title
        if ytitle == None:
            ytitle = 'ytitle' #Default title
        zz = pd.DataFrame(zz, index = rangey, columns= rangex)
        return stlabmtx(zz, xtitle=xtitle, ytitle=ytitle, ztitle=ztitle)

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
            zz = zz.transpose()
            xx = []
            for line in data:
                xx.append(line[xkey].iloc[0])

        #Case of y slow
        #if x is slow, matrix is already correct
        if yslow:
            yy = []
            for line in data:
                yy.append(line[ykey][0])
        xx = np.asarray(xx)
        yy = np.asarray(yy)
        #Sort out titles
        titles = tuple(data[0])
        print(titles)
        print(ykey)
        print(xkey)
        if xtitle == None:
            xtitle = str(xkey) #Default title
        if ytitle == None:
            ytitle = str(ykey) #Default title

        zz = pd.DataFrame(zz)
        zz.index = yy
        zz.columns = xx
        return stlabmtx(zz, xtitle=xtitle, ytitle=ytitle, ztitle=ztitle)

    #Mixed cases (one key and one range) are not implemented
    else:
        print('dictarr_to_mtx: Warning, invalid keys and ranges.  Using defaults')
        if xtitle == None:
            xtitle = 'xtitle' #Default title
        if ytitle == None:
            ytitle = 'ytitle' #Default title
        zz = pd.DataFrame(np.matrix(zz))
        return stlabmtx(zz, xtitle=xtitle, ytitle=ytitle, ztitle=ztitle)
    return





'''
def xderiv(data,rangex,direction=1,axis=1):
    dx = np.abs(rangex[0]-rangex[1])
    if direction==-1:
        dx = -dx
    z = np.squeeze(np.array(data))
    dz = np.gradient(z, dx, axis=axis)    
    return np.matrix(np.squeeze(dz))
'''
 
# Use slow if spacing is non-uniform
'''
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
'''
#Main stlabmtx class

'''
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
    def crop(data,left=None,right=None,up=None,low=None):
        #TODO check
        valdict={'left':left,'right':right,'up':up,'low':low}
        for key,val in valdict.items():
            if val==0:
                valdict[key] = None
            else:
                valdict[key] = int(val)
        data.pmtx = data.pmtx[valdict['left']:valdict['right'],valdict['up']:valdict['low']]
        data.rangex = data.rangex[valdict['up']:valdict['low']]
        data.rangey = data.rangey[valdict['left']:valdict['right']]
        for key,val in valdict.items():
            if val==None:
                valdict[key] = 0
        data.processlist.append('crop {},{},{},{}'.format(valdict['left'],valdict['right'],valdict['up'],valdict['low']))
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
    def lowpass(self,x=0,y=0):
        # TODO implement different filter types
        self.pmtx = np.matrix(gaussian_filter(np.squeeze(np.asarray(self.pmtx)),sigma=[int(y),int(x)]))
        self.processlist.append('lowpass {},{}'.format(x,y))
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
    def sub_lbl(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        self.pmtx = sub_lbl(self.pmtx,lowp,highp,low_limit,high_limit)
        self.processlist.append('sub_lbl {},{},{},{}'.format(lowp,highp,low_limit,high_limit))
    def sub_cbc(self,lowp=40, highp=40, low_limit=-1e99, high_limit=1e99):
        self.pmtx = sub_lbl(self.pmtx.T,lowp,highp,low_limit,high_limit).T
        self.processlist.append('sub_cbc {},{},{},{}'.format(lowp,highp,low_limit,high_limit))
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
    def transpose(self):
        self.pmtx = self.pmtx.T
        self.xtitle, self.ytitle = self.ytitle, self.xtitle
        self.rangex, self.rangey = self.rangey, self.rangex
        self.processlist.append('transpose')
    
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
'''
