"""Module with data writing function definitions

This module includes several functions used in writing data to files in a 
well defined way.  While you are free to write data to a file in any way you want,
it is preferable to try to keep a lab wide standard by using these methods.

The module was written early on and could probably do with some cleanup...  Specifically
old style format strings as well as redundant methods no longer required.

"""
import numpy as np
import os

def writematrix(myfile,mat,f='%.10e',delim=', ',blocksep='\n'):
    """Write a matrix to a given file

    Writes a matrix to a file with a given format specifier and a delimiter.  Adds a block
    separator at the end.  This is very similar to np.savetxt.  However, since python3
    np.savetxt requires the file to be open in binary write mode.

    This function is used internally by both :any:`writedict` and :any:`writeframe`

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    mat : list or np.array
        List containing the lines of data to be written as lists (a matrix or list of lists).
    f : str, optional
        Format specifier for the data (old style).
    delim : str, optional
        Field delimiter (separation character)
    blocksep : str, optional
        Characters to write at the end of the matrix.  This is generally a single newline to
        separate blocks of data.

    """
    for line in mat:
        line = ['%.10e' % x for x in line]
        line = delim.join(line)
        myfile.write(line+'\n')
    myfile.write(blocksep)
    
def writedict(myfile,mydict,f='%.10e',delim=', ',blocksep='\n'):
    """Write a data dictionary to a file as a matrix block

    Writes a given dictionary where each element is a list of numbers, i.e., each element in
    the dict is though of as a column.  Expects all columns to be the same length.
    Also, if the file is empty (no writes have been yet performed on it), it will use the 
    dictionary keys to write the title line.

    Internally this function converts the dict to a matrix and uses :py:func:`stlab.utils.writematrix.writematrix` to save
    to the file.

    The main stlab import renames this function to :code:`stlab.savedict`

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    mydict : dict
        Dict containing the data.  Each element should be a data column.
    f : str, optional
        Format specifier for the data (old style).
    delim : str, optional
        Field delimiter (separation character)
    blocksep : str, optional
        Characters to write at the end of the matrix.  This is generally a single newline to
        separate blocks of data.

    """
    vv = list(mydict.keys())
    writetitle(myfile,vv,delim)
    mat = []
    for nn in mydict.keys():
        mat.append(mydict[nn])
    mat = np.asarray(mat)
    mat = mat.T
    writematrix(myfile,mat,f,delim,blocksep)

def writeparnames(myfile,params,delim=', '):
    """Writes fit parameter names to file

    Intended for writing fit parameter names given a lmfit.Parameters object to a file.

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    params : lmfit.Parameters
        Parameters object input from fit
    delim : str, optional
        Field delimiter (separation character)

    """
    myfile.write('#' + delim.join(params.keys()) + '\n')
    return

def writeparams(myfile,params,f='%.10e',delim=', '):
    """Writes fit parameter values to file

    Intended for writing fit parameter values given a lmfit.Parameters object to a file.

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    params : lmfit.Parameters
        Parameters object input from fit
    delim : str, optional
        Field delimiter (separation character)

    """
    myfile.write(params_to_str(params,f,delim) + '\n')
    return

def params_to_str(params,f='%.10e',delim=', '):
    """Converts fit parameter values to a single line string

    Takes a lmfit.Parameters object and converts its parameter values to a single line string.

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    params : lmfit.Parameters
        Parameters object input from fit
    delim : str, optional
        Field delimiter (separation character)

    Returns
    -------
    str
        Joined string will all parameters

    """
    line = [f % x for x in [params[label].value for label in params.keys()] ]
    return delim.join(line)

def writedictarray(myfile,mydictarray,f='%.10e',delim=', ',blocksep='\n'):
    """Writes an array of data dictionaries to a file

    Intended for writing a list of dictionaries containing the data columns as elements to a file.
    Essentially just repeats :any:`writedict` on every element of the list making sure to include the
    title line (derived from the first dictionarly key values) if the file is new.

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    mydictarray : list of dict
        List containing the Dicts to be written.
    f : str, optional
        Format specifier for the data (old style).
    delim : str, optional
        Field delimiter (separation character)
    blocksep : str, optional
        Characters to write at the end of the matrix.  This is generally a single newline to
        separate blocks of data.

    """
    vv = list(mydictarray[0].keys())
    writetitle(myfile,vv,delim)
    for block in mydictarray:
        writedict(myfile,block,f,delim,blocksep)
    return

#???
def writeline(myfile,line,f='.10e',delim=', '):
    """Writes a list of numbers as a single line to a file

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    line : list of float
        List containing the numbers to be written
    f : str, optional
        Format specifier for the data (new style).
    delim : str, optional
        Field delimiter (separation character)

    """
    for x in line[:-1]:
        myfile.write("{:{form}}".format(x,form = f) + delim)
    myfile.write("{:{form}}\n".format(line[-1],form = f))
    myfile.flush()
    return
#???

def writeframe(myfile,myframe,f='%.10e',delim=', ',blocksep='\n'):
    """Write a pandas Dataframe to a file as a matrix block

    Writes a given pandas.DataFrame to a file.  Is analogous to :any:`writedict`
    Also, if the file is empty (no writes have been yet performed on it), it will use the 
    dataframe column indexes to write the title line.

    Internally this function converts just writes the matrix using :py:func:`stlab.utils.writematrix.writematrix`

    The main stlab import renames this function to :code:`stlab.saveframe`

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    mydict : dict
        Dict containing the data.  Each element should be a data column.
    f : str, optional
        Format specifier for the data (old style).
    delim : str, optional
        Field delimiter (separation character)
    blocksep : str, optional
        Characters to write at the end of the matrix.  This is generally a single newline to
        separate blocks of data.

    """
    vv = list(myframe)
    writetitle(myfile,vv,delim)
    mat = myframe.values
    writematrix(myfile,mat,f,delim,blocksep)

def writeframearray(myfile,myframearray,f='%.10e',delim=', ',blocksep='\n'):
    """Writes an array of pandas DataFrame to a file

    Analogous to :any:`writedictarray` but using pd.Dataframe instead of dicts.  Expects a list of
    pd.DataFrames to be written to the file.  Also handles writing the title line if the file is
    new.

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    mydictarray : list of dict
        List containing the Dicts to be written.
    f : str, optional
        Format specifier for the data (old style).
    delim : str, optional
        Field delimiter (separation character)
    blocksep : str, optional
        Characters to write at the end of the matrix.  This is generally a single newline to
        separate blocks of data.

    """
    vv = list(myframearray[0])
    writetitle(myfile,vv,delim)
    for block in myframearray:
        writeframe(myfile,block,f,delim,blocksep)
    return

def writetitle(myfile,vv,delim):
    """Given a list of strings writes the file title line

    Does not do anything if the file already has contents.  Includes a '#' as first character for
    gnuplot.  Is used by :any:`writedict` and :any:`writeframe`.

    Parameters
    ----------
    myfile : _io.TextIOWrapper
        Open file handle for writing
    vv : list of str
        List of column titles
    delim : str, optional
        Field delimiter (separation character)

    """
    #myfile.flush()
    if myfile.tell() == 0: #Is the file new?  If so, write title line from provided data
        varline = '#' + delim.join(vv) + '\n'
        myfile.write(varline)
