"""Method for opening a new file for writing

This module contains a single method used for creating a new datafile.  This method
handles timestamping the measurement folder, keeping track of the index of the measurement
(if desired) and makes backup copies of the previously run scripts for reference.

"""
import datetime
import os
import shutil
import re
from stlab.utils import getgitid

# Creates new measurement folder using prefix + datetime + idstring.
# If colnames (array of column names) is included, the title line is written
# Also copies main script file to measurement folder


def newfile(prefix,
            idstring,
            colnames=None,
            mypath='./',
            usedate=True,
            usefolder=True,
            autoindex=False,
            return_folder_name=False,
            git_id=True):
    """Creates a new file for storing data.

    By default will create a folder (at the location of the running script) with a new file open for writing
    and a copy of the script the function was called from.  The naming scheme for the folder is :code:`<prefix>_yy_mm_dd_HH.MM.SS_<idstring>`.
    The file is named the same with a ".dat" extension.

    Generally, if using default options, overwriting an existing file should not happen (date and time will never be exactly equal).
    However, if the desired filename already exists, this method will overwrite the old file.

    Parameters
    ----------
    prefix : str
        A string to be placed in front of the timestamp in the filename.  Can be blank or None but must be specified
    idstring : str
        A string to be placed behind the timestamp.  Can also be blank or None but must be specified
    colnames : list of str, optional
        Array-like containing column titles for data.  This will be written in the first line of the file delimited by ', '.
        As an example, if colnames = ['abc', 'def', 'ghi'], the first line in the file will be :code:`\"# abc, def, ghi\\n\"`.  By default is left blank
    mypath : str, optional
        Path for folder (or file) creation if pwd is not the desired path.  By default it is pwd.
    usedate : bool, optional
        Boolean to include timestamp.  If False, the timestamp is excluded from the file/folder name.  True by default
    usefolder : bool, optional
        If set to False the file will be opened at the specified location with the usual naming but with no
        subfolder and no copy will be made of the running script.  True by default
    autoindex : bool, optional
        Specifies if indexing of successively opened files is desired.  Will add a running index to the prefix of the newly created file/folder.
        This will be incremented by 1 for each new file with the same prefix.  If no files are found with the same prefix, it creates the
        first file name <prefix>1_yy_mm_dd_HH.MM.SS_<idstring>.  Successive files will be named <prefix><idx>_yy_mm_dd_HH.MM.SS_<idstring>.
        Is False by default.
    git_id : bool, optional
        Boolean to query and save the git id of stlab

    Returns
    -------
    myfile : _io.TextIOWrapper
        Open file handle for writing

    """
    import __main__
    if hasattr(__main__, '__file__'):
        mainfile = __main__.__file__
    else:
        mainfile = None
    print(mainfile)
    mytime = datetime.datetime.now()
    datecode = '%s' % mytime.year + '_' + (
        '%s' % mytime.month).zfill(2) + '_' + ('%s' % mytime.day).zfill(2)
    timecode = ('%s' % mytime.hour).zfill(2) + '.' + (
        '%s' % mytime.minute).zfill(2) + '.' + ('%s' % mytime.second).zfill(2)

    # Autoindexing...  Prefix is followed by an incremental index.
    # Looks for already present files/folders with the same prefix and indexes and creates the next index.
    # If none are found, starts with the first.

    if autoindex:
        if (prefix == '' or prefix == None):
            raise ValueError('No prefix given for autoindexing')
        namelist = [name for name in os.listdir(mypath)]
        idxs = []
        pattern = '^' + prefix + '\\d+$'
        pattern = re.compile(pattern)
        for name in namelist:
            name = name.split('_')[0]
            match = pattern.match(name)
            if match:
                nn = int(name[len(prefix):])
                idxs.append(nn)
        if idxs:
            prefix = prefix + str(max(idxs) + 1)
        else:
            prefix = prefix + '1'

    if usedate:
        foldername = prefix + '_' + datecode + '_' + timecode + '_' + idstring
    else:
        foldername = prefix + '_' + idstring

    #Check if prefix or idstring are blank and remove unnecessary underscores
    if (idstring == '' or idstring == None):
        foldername = foldername[:-1]
    if (prefix == '' or prefix == None):
        foldername = foldername[1:]
    if len(foldername) == 0:
        raise ValueError(
            'No name given... Add at least a prefix or idstring or date')

    filename = foldername + '.dat'

    if usefolder:
        fullfoldername = os.path.normpath(mypath + '/' + foldername)
        fullfilename = os.path.normpath(mypath + '/' + foldername + '/' +
                                        filename)
    else:
        fullfoldername = os.path.normpath(mypath + '/')
        fullfilename = os.path.normpath(mypath + '/' + filename)
    print(fullfoldername)
    print(fullfilename)
    if not os.path.exists(fullfoldername):
        os.makedirs(fullfoldername)
    print('Measurement Name: ', foldername)
    if mainfile != None and usefolder:
        scriptname = os.path.basename(mainfile)
        shutil.copyfile(mainfile,
                        os.path.normpath(fullfoldername + '/' + scriptname))
    myfile = open(fullfilename, 'w')
    if colnames is not None:
        varline = '#' + ', '.join(colnames) + '\n'
        myfile.write(varline)
    if git_id:
        try:
            getgitid.get_gitid(myfile)
        except subprocess.CalledProcessError as e:
            print("##################\nget_gitid failed:\n", e.output)
        except FileNotFoundError:
            print("##################\nget_gitid failed:\nYour stlab(utils) is most likely not a git repo but was downloaded")
    if return_folder_name:
        return myfile, fullfoldername
    else:
        return myfile
