"""Autoplotting measurements

Function definition for simple plotting routine to be run at end of mesurement

"""

import matplotlib.pyplot as plt
import stlab
import os
import traceback
import logging
from functools import wraps


def catchexception(func):
    @wraps(func)
    def overfunc(*args,**kwargs):
        try:
            func(*args,**kwargs)
        except Exception as e:
            logging.error(traceback.format_exc())
            print('Continuing...')
    return overfunc

@catchexception
def autoplot(datafile,xlab,ylab,zlab=None,title='YOU SHOULD ADD A TITLE',caption='YOU SHOULD ADD A COMMENT',show=False,**kwargs):
    """Autoplot function

    Takes a data file handle (still open or recently closed) or a filename and plots the requested
    columns).  Saves figure as a png alongside the original data file with the same name.
    As a precaution, if an exception is raised during the execution of this function, it will be caught internally
    so as not to interrupt the caller.

    Parameters
    ----------
    datafile : _io.TextIOWrapper or str
        Data file handle (can be open or closed) or data file name for reading
    xlab : str
        Label for x axis data
    ylab : str
        Label for y axis data
    zlab : str or None, optional
        Label for z axis data.  If set to none, a line plot is returned.  If set to str
        a color plot is returned
    title : str, optional
        Text label to be included in the title
    caption : str, optional
        Comment included below figure
    **kwargs
        Arguments to be passed to plotting function (plt.plot or plt.imshow)

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

    fig = plt.figure(figsize=(10,8))
    ax1 = fig.add_axes((0.2, 0.2, 0.8, 0.7))

    if zlab is None:
        for line in data:
            plt.plot(line[xlab],line[ylab],**kwargs)
    else:
        mymtx = stlab.framearr_to_mtx(data, zlab, xkey=xlab, ykey=ylab)
        plt.imshow(mymtx.pmtx, aspect='auto', cmap='seismic', extent=mymtx.getextents(), **kwargs)
        cbar = plt.colorbar()
        cbar.set_label(zlab)
    plt.title(os.path.basename(fname) + '\n' + title,fontsize = 10)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.figtext(0.5, 0.05, caption, wrap=True, horizontalalignment='center', fontsize=10)
    plt.savefig(basename+'.png',dpi=600)
    if show:
        plt.show()
    plt.close()



