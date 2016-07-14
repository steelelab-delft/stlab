import os
import readdata

def fromarrays(filename,xarray,yarray,zarray=None,xtitle='',ytitle='',ztitle='',colnames=None):
    Nx = len(xarray)
    xmin = xarray[0]
    xmax = xarray[-1]
    Ny = len(yarray)
    ymin = yarray[0]
    ymax = yarray[-1]
    if zarray == None:
        Nz = None
        zmin = None
        zmax = None
    else:
        Nz = len(zarray)
        zmin = zarray[0]
        zmax = zarray[-1]
    fromlimits(filename,Nx,xmin,xmax,Ny,ymin,ymax,Nz,zmin,zmax,xtitle,ytitle,ztitle,colnames)
    return

def fromlimits(filename,Nx,xmin,xmax,Ny,ymin,ymax,Nz=None,zmin=None,zmax=None,xtitle='',ytitle='',ztitle='',colnames=None):
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
    f.write(str(ymin)+'\n')
    f.write(str(ymax)+'\n')
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
        for i,name in enumerate(colnames):
            f.write(str(i+1)+'\n')
            f.write(str(name)+'\n')
        f.close()
    return


#Somewhat specific for datafiles from the solderroom, 2D files only
def fromdatafile(filename,xcol=None,ycol=None,xtitle=None,ytitle=None):
    mydata = readdata.readdat(filename)
    keylist = mydata[0].keys()

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
    ymin = mydata[0][ykey][0]
    ymax = mydata[-1][ykey][0]

    print Nx,xmin,xmax
    print Ny,ymin,ymax

    fromlimits(filename,Nx,xmin,xmax,Ny,ymin,ymax,xtitle=xkey,ytitle=ykey,colnames=keylist)
    return






