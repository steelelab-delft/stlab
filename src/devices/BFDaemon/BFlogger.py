import time
import datetime
from queue import Queue
from stlab.devices.Lakeshore_370 import Lakeshore_370
import os

SLEEPTIME = 30.


def BFlogger(commandq, addr, port, logpath="D:/BF/logs"):

    resultq = Queue(maxsize=0)
    today = datetime.date.today()

    chs = [1, 2, 5, 6]
    labs = ['T', 'R']
    lls = [(x, y) for x in chs for y in labs]
    ffs = []
    foldername = logpath + './' + today.strftime('%y-%m-%d') + '/'
    for i, lab in lls:
        filename = foldername + 'CH{} '.format(i) + '{} '.format(
            lab) + today.strftime('%y-%m-%d') + '.log'
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        print('File CH{} {}: '.format(i, lab), filename)
        ff = open(filename, 'ba+')
        if ff.tell() > 0:
            ff.seek(-1, 2)
            ch = ff.read().decode()
            if ch != '\n':
                ff.write(os.linesep)
        ffs.append(ff)

    # Main logging loop.  Exit with keyboard interrupt (CTRL + C)
    try:
        while True:
            print('Time: ' + time.strftime('%c'))
            print('Current IP: ' + addr)
            print('Current Port: ' + str(port))
            newday = datetime.date.today()
            if today != newday:
                print('New day: {}'.format(newday.strftime('%y-%m-%d')))
                for ff in ffs:
                    ff.close()
                ffs = []
                today = newday
                for i, lab in lls:
                    foldername = './' + today.strftime('%y-%m-%d') + '/'
                    filename = foldername + 'CH{} {} '.format(
                        i, lab) + today.strftime('%y-%m-%d') + '.log'
                    if not os.path.exists(foldername):
                        os.makedirs(foldername)
                    print('File CH{} {}: '.format(i, lab), filename)
                    ff = open(filename, 'ba+')
                    if ff.tell() > 0:
                        ff.seek(-1, 2)
                        ch = ff.read().decode()
                        if ch != '\n':
                            ff.write(os.linesep)
                    ffs.append(ff)

            current_time = datetime.datetime.now()
            for ff, (i, lab) in zip(ffs, lls):
                line = []
                line.append(current_time.strftime(' %d-%m-%y'))
                line.append(current_time.strftime('%H:%M:%S'))
                if lab == 'T':
                    commandq.put((resultq, Lakeshore_370.GetTemperature,
                                  (i, )))
                elif lab == 'R':
                    commandq.put((resultq, Lakeshore_370.GetResistance, (i, )))
                xx = resultq.get()
                resultq.task_done()
                line.append('{:e}'.format(xx))
                line = ','.join(line) + os.linesep
                ff.write(line.encode('ascii'))
                ff.flush()
            time.sleep(SLEEPTIME)
    except KeyboardInterrupt:
        for ff in ffs:
            ff.close()
    print('Goodbye!')
