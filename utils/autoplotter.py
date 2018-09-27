"""Autoplotting measurements

Function definition for simple plotting routine to be run at end of mesurement

"""

import matplotlib.pyplot as plt
import stlab
import os

def autoplot(datafile,xlab,ylab,zlab=None,show=True,**kwargs):
    """Autoplot function

    Takes a data file handle (still open or recently closed) or a filename and plots the requested
    columns).  Saves figure as a png alongside the original data file with the same name.


    Parameters
    ----------
    datafile : _io.TextIOWrapper or str
        Data file handle (can be open or closed) or data file name for reading
    xlab : str
        Label for x axis data
    ylab : str
        Label for y axis data
    zlab : str or None
        Label for z axis data.  If set to none, a line plot is returned.  If set to str
        a color plot is returned
    **kwargs
        Arguments to be passed to plotting function (plt.plot or plt.imshow)
     
    Returns
    -------
    None
        Does not return any value

    """
    try:
        datafile.flush()
        fname = datafile.name
    except AttributeError:
        fname = datafile
    except ValueError:
        fname = datafile.name
    data = stlab.readdata.readdat_pd(fname)
    basename = os.path.splitext(fname)[0]

    if zlab is None:
        for line in data:
            plt.plot(line[xlab],line[ylab],**kwargs)
    else:
        mymtx = stlab.framearr_to_mtx(data, zlab, xkey=xlab, ykey=ylab)
        plt.imshow(mymtx.pmtx, aspect='auto', cmap='seismic', extent=mymtx.getextents(), **kwargs)
        cbar = plt.colorbar() 
        cbar.set_label(zlab)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.savefig(basename+'.png',dpi=600)
    plt.show()
