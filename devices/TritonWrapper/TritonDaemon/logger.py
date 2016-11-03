#This script simply retrieves temperature and pressure data from the Triton control computer and writes
#the data to a simple ascii file.

import time
import datetime
from queue import Queue
from stlab.devices.triton import Triton

def logger(commandq,ff):
    resultq = Queue(maxsize=0)
    
    # Main logging loop.  Exit with keyboard interrupt (CTRL + C)
    try:
        while True:
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
    return