#This script simply retrieves temperature and pressure data from the Triton control computer and writes
#the data to a simple ascii file.

import time
import datetime
from queue import Queue
from stlab.devices.triton import Triton
import os

varline = ['Time (s)'] + ['PT2 Head (K)','PT2 Plate (K)', 'Still Plate (K)','Cold Plate (K)','MC Cernox (K)','PT1 Head (K)','PT1 Plate (K)','MC Plate (K)'] + ['P%d (mbar)' % i for i in range(1,7)]

def logger(commandq):
    
    resultq = Queue(maxsize=0)
    today = datetime.date.today()
    foldername = './' + today.strftime('%Y-%m-%d') + '/' 
    filename = foldername + 'log_' + today.strftime('%Y-%m-%d')+ '.dat'
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    print('Measurement Folder: ', foldername)
    if os.path.isfile(filename):
        ff = open(filename,'a')
    else:
        ff = open(filename,'w')
        ff.write('#' + ', '.join(varline)+'\n')
      
    
    
    # Main logging loop.  Exit with keyboard interrupt (CTRL + C)
    try:
        while True:
            newday = datetime.date.today()
            if today != newday:
                    ff.close()
                    today = newday
                    foldername = './' + today.strftime('%Y-%m-%d') + '/' 
                    filename = foldername + 'log_' + today.strftime('%Y-%m-%d')+ '.dat'
                    if not os.path.exists(foldername):
                        os.makedirs(foldername)
                    print('New day - Measurement Folder: ', foldername)
                    if os.path.isfile(filename):
                        ff = open(filename,'a')
                    else:
                        ff = open(filename,'w')
                        ff.write('#' + ', '.join(varline)+'\n')
            line = []
            for i in range(1,10):
                commandq.put( (resultq, Triton.gettemperature, (i,)) )
                xx = resultq.get()
                line.append(xx)
                resultq.task_done()
            for i in range(1,7):
                commandq.put( ( resultq, Triton.getpressure, (i,) ) )
                xx = resultq.get()
                line.append(xx)
                resultq.task_done()
            t = datetime.datetime.now()
            print(t)
            t = t.replace(tzinfo=datetime.timezone.utc).timestamp() #To correct for the fact that we are not in UTC time zone
            # Could produce strange results when DST is applied (an hour of repeated or missing time stamps).
            print('Timestamp: ',t)
            line.insert(0,t)
            for j,x in enumerate(line):
                if j==len(line)-1:
                    ff.write('%.10e' % x + '\n')
                else:
                    ff.write('%.10e' % x + ', ')
            ff.flush()
            time.sleep(30)
    except KeyboardInterrupt:
        ff.close()
    print('Goodbye!')