import os
from . import readdata
import numpy as np


def fromarrays(myfile,xarray,yarray,zarray=[],xtitle='',ytitle='',ztitle='',colnames=None):
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






