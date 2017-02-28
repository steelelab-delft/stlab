import datetime
import os
import shutil

# Creates new measurement folder using prefix + datetime + idstring.
# If colnames (array of column names) is included, the title line is written
# Also copies main script file to measurement folder

def newfile(prefix,idstring,colnames=None,mypath = './',usedate=True):

    import __main__
    if hasattr(__main__, '__file__'):
        mainfile = __main__.__file__
    else:
        mainfile = None
    print(mainfile)
    mytime = datetime.datetime.now()
    datecode = '%s' % mytime.year + '_' + ('%s' % mytime.month).zfill(2) + '_' +('%s' % mytime.day).zfill(2)
    timecode = ('%s' % mytime.hour).zfill(2) +'.' + ('%s' % mytime.minute).zfill(2) +'.' + ('%s' % mytime.second).zfill(2)

    if usedate:
        foldername = prefix + '_' + datecode+'_'+timecode+'_'+idstring
    else:
        foldername = prefix + '_' +idstring
    filename = foldername+'.dat'
    fullfoldername = os.path.normpath(mypath + '/' + foldername)
    fullfilename = os.path.normpath(mypath + '/' + foldername + '/' + filename)
    print(fullfoldername)
    print(fullfilename)
    if not os.path.exists(fullfoldername):
        os.makedirs(fullfoldername)
    print('Measurement Folder: ', foldername)
    if mainfile !=None:
        scriptname = os.path.basename(mainfile)
        shutil.copyfile(mainfile,os.path.normpath(fullfoldername + '/' + scriptname))
    myfile = open(fullfilename, 'w')
    if colnames!=None:
        varline = '#' + ', '.join(colnames) + '\n'
        myfile.write(varline)
    return myfile
