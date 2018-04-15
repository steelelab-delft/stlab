import datetime
import os
import shutil
import re

# Creates new measurement folder using prefix + datetime + idstring.
# If colnames (array of column names) is included, the title line is written
# Also copies main script file to measurement folder

def newfile(prefix,idstring,colnames=None,mypath = './',usedate=True,usefolder=True, autoindex = False):

    import __main__
    if hasattr(__main__, '__file__'):
        mainfile = __main__.__file__
    else:
        mainfile = None
    print(mainfile)
    mytime = datetime.datetime.now()
    datecode = '%s' % mytime.year + '_' + ('%s' % mytime.month).zfill(2) + '_' +('%s' % mytime.day).zfill(2)
    timecode = ('%s' % mytime.hour).zfill(2) +'.' + ('%s' % mytime.minute).zfill(2) +'.' + ('%s' % mytime.second).zfill(2)

    # Autoindexing...  Prefix is followed by an incremental index.
    # Looks for already present files/folders with the same prefix and indexes and creates the next index.
    # If none are found, starts with the first.
    
    if autoindex:
        if (prefix == '' or prefix == None):
            raise ValueError('No prefix given for autoindexing')
        namelist = [name for name in os.listdir(".")]
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
            prefix = prefix + str(max(idxs)+1)
        else:
            prefix = prefix + '1'
    
    if usedate:
        foldername = prefix + '_' + datecode+'_'+timecode+'_'+idstring
    else:
        foldername = prefix + '_' +idstring

    #Check if prefix or idstring are blank and remove unnecessary underscores
    if (idstring == '' or idstring == None):
        foldername = foldername[:-1]
    if (prefix == '' or prefix == None):
        foldername = foldername[1:]
    if len(foldername)==0:
        raise ValueError('No name given... Add at least a prefix or idstring or date')

    filename = foldername+'.dat'


    if usefolder:
        fullfoldername = os.path.normpath(mypath + '/' + foldername)
        fullfilename = os.path.normpath(mypath + '/' + foldername + '/' + filename)
    else:
        fullfoldername = os.path.normpath(mypath + '/')
        fullfilename = os.path.normpath(mypath + '/' + filename)
    print(fullfoldername)
    print(fullfilename)
    if not os.path.exists(fullfoldername):
        os.makedirs(fullfoldername)
    print('Measurement Name: ', foldername)
    if mainfile !=None and usefolder:
        scriptname = os.path.basename(mainfile)
        shutil.copyfile(mainfile,os.path.normpath(fullfoldername + '/' + scriptname))
    myfile = open(fullfilename, 'w')
    if colnames!=None:
        varline = '#' + ', '.join(colnames) + '\n'
        myfile.write(varline)
    return myfile

    
