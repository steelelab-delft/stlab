import os
def metagen(filename,xarray,yarray,zarray=None,xtitle='',ytitle='',ztitle='',colnames=None):
    Nx = len(xarray)
    Ny = len(yarray)
    xmin = xarray[0]
    xmax = xarray[-1]
    ymin = yarray[0]
    ymax = yarray[-1]
    base, ext = os.path.splitext(filename)
    metaname = base + '.meta.dat'
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
    if zarray == None:
        f.write('#No loop, Z\n')
        f.write(str(1)+'\n')
        f.write(str(0)+'\n')
        f.write(str(1)+'\n')
        f.write('Nothing\n')
    else:
        Nz = len(zarray)
        zmin = zarray[0]
        zmax = zarray[-1]
        f.write('#Outer outer loop, Z\n')
        f.write(str(Nz)+'\n')
        f.write(str(zmin)+'\n')
        f.write(str(zmax)+'\n')
        f.write(str(ztitle)+'\n')

    f.write('#Column labels\n')
    if colnames!=None:
        for i,name in enumerate(colnames):
            f.write(str(i)+'\n')
            f.write(str(name)+'\n')
        f.close()

    return

