"""Module for generation of spyview metafiles

Spyview typically requires an additional metafile to correctly label the axes and labels
of a dataset.  The meta file structure is detailed at 
`Spyview <http://nsweb.tn.tudelft.nl/~gsteele/spyview/>`_.

Given a dataset, the metafile contains the x,y axis start, end and number of points as well
as column titles.  This means that spyview can only handle uniformly spaced axes.
It can also contain z axis start, stop and number of points for data cubes
but this is rarely used so it is generally left with 1 point (single 2d plot).
This z axis is NOT the data axis.

The module provides a few different functions for generating the axes limits and metafile from your data.
It is important to keep in mind that in general spyview does not treat any of the columns in the
file as special in any way.  It only reads the requested column and tries to reshape it into a matrix
to display in the final color plot.  The metafile tells spyview how this reshaping should be done, i.e,
how many points are on x and y and how it should label the axis values and titles.  When importing without
a metafile, spyview searches for blank lines to figure out when each line of the matrix ends.

"""


import os
from . import readdata
import numpy as np


def fromarrays(myfile,xarray,yarray,zarray=[],xtitle='',ytitle='',ztitle='',colnames=None):
    """Generates a metafile for a given file using axes arrays as input

    Generates a metafile for the given file taking the endponts of given arrays and their length.
    Column titles are added manually providing a list of titles or by autogenerating from the
    file title line.

    Internally, this function calls :any:`fromlimits`

    Parameters
    ----------
    myfile : file or string
        Base file for metafile
    xarray : array of floats
        Array for x axis limits and number of points
    yarray : array of floats
        Array for y axis limits and number of points
    zarray : array of floats or empty list, optional
        Array for z axis limits and number of points (for data cubes)
    xtitle, ytitle, ztitle : str, optional
        Title for x, y, z axis axis
    colnames : list of str, 'auto' or None, optional
        List of column titles for the given file.  If None, no titles are written in metafile.  If auto
        function reads the first line of the file and uses the obtained titles in the metafile

    """

    xarray = np.array(xarray)
    yarray = np.array(yarray)
    zarray = np.array(zarray)
    Nx = len(xarray)
    xmin = xarray[0]
    xmax = xarray[-1]
    if xmin == xmax:
        xmax = xmin + 1
        print('metagen.fromarrays: Warning, equal values for xmin and xmax. Correcting')
    Ny = len(yarray)
    ymax = yarray[-1]
    ymin = yarray[0]
    if ymin == ymax:
        ymax = ymin +1
        print('metagen.fromarrays: Warning, equal values for ymin and ymax. Correcting')
    if len(zarray) == 0:
        Nz = None
        zmin = None
        zmax = None
    else:
        zarray = np.array(zarray)
        Nz = len(zarray)
        zmin = zarray[0]
        zmax = zarray[-1]
        if zmin == zmax:
            zmax = zmin +1
            print('metagen.fromarrays: Warning, equal values for zmin and zmax. Correcting')
    fromlimits(myfile,Nx,xmin,xmax,Ny,ymin,ymax,Nz,zmin,zmax,xtitle,ytitle,ztitle,colnames)
    return

def fromlimits(myfile,Nx,xmin,xmax,Ny,ymin,ymax,Nz=None,zmin=None,zmax=None,xtitle='',ytitle='',ztitle='',colnames=None):
    """Generates a metafile for the given axis limits and point number

    Generates a metafile for the given file taking the endponts of given arrays and their length.
    Column titles are added manually providing a list of titles or by autogenerating from the
    file title line.

    Internally, this function is called by :any:`fromarrays`.

    Parameters
    ----------
    myfile : file or string
        Base file for metafile
    Nx, Ny : int
        Number of points in x, y axis
    Nz : int or None, optional
        Number of points in z axis
    xmin, ymin : float
        Minimum value for x and y axis
    xmax, ymax : float
        Maximum value for x and y axis
    zmin, zmax : float or None, optional
        Maximum and minimum value for the z axis (for data cubes)
    xtitle, ytitle, ztitle : str, optional
        Title for x, y, z axis axis
    colnames : list of str, 'auto' or None, optional
        List of column titles for the given file.  If None, no titles are written in metafile.  If auto
        function reads the first line of the file and uses the obtained titles in the metafile

    """
    if isinstance(myfile, str):
        filename = myfile
    else:
        filename = os.path.realpath(myfile.name)
    base, ext = os.path.splitext(filename)
    metaname = base + '.meta.txt'
    f = open(metaname,'w')

    f.write('#Inner loop, X\n')
    f.write(str(Nx)+'\n')
    f.write(str(xmin)+'\n')
    f.write(str(xmax)+'\n')
    f.write(str(xtitle)+'\n')
    f.write('#Outer loop, Y\n')
    f.write(str(Ny)+'\n')
#    f.write(str(ymin)+'\n')
#    f.write(str(ymax)+'\n')
    f.write(str(ymax)+'\n')
    f.write(str(ymin)+'\n')
    f.write(str(ytitle)+'\n')
    if Nz == None:
        f.write('#No loop, Z\n')
        f.write(str(1)+'\n')
        f.write(str(0)+'\n')
        f.write(str(1)+'\n')
        f.write('Nothing\n')
    else:
        f.write('#Outer outer loop, Z\n')
        f.write(str(Nz)+'\n')
        f.write(str(zmin)+'\n')
        f.write(str(zmax)+'\n')
        f.write(str(ztitle)+'\n')
    f.write('#Column labels\n')
    if colnames!=None:
        if colnames == 'auto':
            ff = open(filename,'r')
            titleline = ff.readline()
            if titleline[0] == '#':
                titleline = titleline[1:]
            colnames = titleline.split(', ')
        else:
            colnames = list(colnames)
        for i,name in enumerate(colnames):
            f.write(str(i+1)+'\n')
            f.write(str(name)+'\n')
        f.close()
    return


#Somewhat specific for datafiles from the solderroom, 2D "gnuplot" files only
def fromdatafile(myfile,xcol=None,ycol=None,xtitle=None,ytitle=None):
    if isinstance(myfile, str):
        filename = myfile
    else:
        filename = os.path.realpath(myfile.name)
    mydata = readdata.readdat(filename)
    keylist = list(mydata[0].keys())

    if (type(xcol) is not int) and (type(ycol) is not int) and (type(xtitle) is str) and (type(ytitle) is str):
        xcol = keylist.index(xtitle)
        ycol = keylist.index(ytitle)
    elif (type(xcol) is not int) and (type(ycol) is int) and (type(xtitle) is str):
        xcol = keylist.index(xtitle)
        ycol = ycol-1
    elif (type(ycol) is not int) and (type(xcol) is int) and (type(ytitle) is str):
        xcol = xcol-1
        ycol = keylist.index(ytitle)
    elif (type(xcol) is int) and (type(ycol) is int):
        xcol=xcol-1
        ycol=ycol-1
        pass
    else:
        raise Exception("metagen.fromdatafile: Bad column specification")

    if (xcol<0 or ycol<0):
        raise Exception("metagen.fromdatafile: Bad column specification")

    xkey = keylist[xcol]
    ykey = keylist[ycol]

    Nx = len(mydata[0][xkey])
    xmin = mydata[0][xkey][0]
    xmax = mydata[0][xkey][-1]
    Ny = len(mydata)
    ymin = mydata[-1][ykey][0]
    ymax = mydata[0][ykey][0]

    print(xkey,Nx,xmin,xmax)
    print(ykey,Ny,ymin,ymax)

    fromlimits(filename,Nx,xmin,xmax,Ny,ymin,ymax,xtitle=xkey,ytitle=ykey,colnames=keylist)
    return






