def metagen(filename,xarray,yarray,zarray=None,xtitle='',ytitle='',ztitle=''):
    Nx = len(xarray)
    Ny = len(yarray)
    xmin = xarray[0]
    xmax = xarray[-1]
    ymin = yarray[0]
    ymax = yarray[-1]
    metaname = filename.rstrip('.dat') + '.meta.dat'
    f = open(metaname,'w')

    f.write(str(Nx)+'\n')
    f.write(str(xmin)+'\n')
    f.write(str(xmax)+'\n')
    f.write(str(Ny)+'\n')
    f.write(str(ymin)+'\n')
    f.write(str(ymax)+'\n')

    if zarray != None:
        Nz 

