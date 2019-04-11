"""Autoplotting measurements

Function definition for simple plotting routine to be run at end of mesurement

"""

import matplotlib.pyplot as plt
import stlab
import os
import traceback
import logging
from functools import wraps
import numpy as np


def catchexception(func):  #Decorator function
    @wraps(
        func
    )  #So that docstrings of the original function are conserved and sphynx works properly
    def overfunc(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.error(traceback.format_exc())
            print('Continuing...')

    return overfunc


@catchexception
def autoplot(
        datafile,
        xlab,
        ylab,
        zlab=None,
        title='YOU SHOULD ADD A TITLE',
        caption='YOU SHOULD ADD A COMMENT',
        show=False,
        dpi=400,
        pl=None,
        cmap='RdBu_r',
        wbval=(0.1, 0.1),  #percent
        figdir=None,
        **kwargs):
    """Autoplot function

    Takes a data file handle (still open or recently closed) or a filename and plots the requested
    columns).  Saves figure as a png alongside the original data file with the same name.
    As a precaution, if an exception is raised during the execution of this function, it will be caught internally
    so as not to interrupt the caller.  It now doesn't overwrite any previous figure.  If a figure file already exists,
    it creates a new file with an index.

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
    show : bool, optional
        Show the plot on screen (blocks execution until closed)
    dpi : int, optional
        dpi for matplotlib savefig function
    pl : list of str, optional
        If provided, is an stlabmtx process list (in case processing is required on a 2d color plot).
        See :class:`stlabmtx <stlab.utils.stlabdict.stlabmtx>` for details
    cmap : str
        Matplotlib colormap string for 2D plots. By default 'RdBu_r'.
        See https://matplotlib.org/tutorials/colors/colormaps.html for details
    figdir : str
        Figure directory for the final plot
    **kwargs
        Other arguments to be passed to plotting function (plt.plot or plt.imshow)

    Returns
    -------
    fig : matplotlib.figure.Figure
        Final figure that has been saved to file

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

    fig = plt.figure(figsize=(10, 8))
    _ = fig.add_axes((0.2, 0.2, 0.75, 0.75))

    if zlab is None:
        for line in data:
            plt.plot(line[xlab], line[ylab], **kwargs)
    else:
        mymtx = stlab.framearr_to_mtx(data, zlab, xkey=xlab, ykey=ylab)
        if pl is not None:
            mymtx.applyprocesslist(pl)
            zlab = zlab + '    (' + ', '.join(pl) + ')'
        lims = np.percentile(mymtx.pmtx.values, (wbval[0], 100 - wbval[1]))
        vmin = lims[0]
        vmax = lims[1]

        plt.imshow(
            mymtx.pmtx,
            aspect='auto',
            cmap=cmap,
            extent=mymtx.getextents(),
            vmin=vmin,
            vmax=vmax,
            **kwargs)
        cbar = plt.colorbar()
        cbar.set_label(zlab)
    plt.title(os.path.basename(fname) + '\n' + title, fontsize=10)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.figtext(
        0.5,
        0.05,
        caption,
        wrap=True,
        horizontalalignment='center',
        fontsize=10)
    if figdir:
        plt.savefig(figdir + basename + '.png', dpi=dpi)
    else:
        if os.path.isfile(basename + '.png'):
            i = 0
            while True:
                if os.path.isfile(basename + str(i) + '.png'):
                    i = i + 1
                    continue
                else:
                    basename = basename + str(i)
                    break
        plt.savefig(basename + '.png', dpi=dpi)
    if show:
        plt.show()
    return fig
