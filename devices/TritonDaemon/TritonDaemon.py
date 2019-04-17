"""Triton Daemon - Communication server for Oxford Triton system

The Triton fridge already has communication capacity to directly control and read both the temperatures and other elements
of the fridge (pressure sensors, valves, compressor, ...).  However, the Triton logging uses binary format files that can
only be opened in their (very flaky) propriety program.  This Daemon acts as an intermediary between the Triton system and
the measurement computer, allowing the measurement computer to send commands to the system while it maintains an ASCII log
of the system parameters.  These logfiles can then be opened using cryoLogger.  Note that the binary logs are still
kept in any case.

Run as::
  
  python TritonDaemon.py

This Daemon is intended to be run on the Triton control computer but can actually be run from any system that has network access
to the triton control computer.  The address will be requested when the script is started as well as the folder where the logs
should be saved.  The defaults can be adjusted in the variables :code:`TRITONADDR` and :code:`LOGFOLDER` at the top of the script.

"""
from stlab.devices.Oxford_Triton import Oxford_Triton as Triton
from queue import Queue
from threading import Thread
import time
from stlab.devices.TritonDaemon.TritonLogger import TritonLogger as logger
import socket
from stlab.utils.MySocket import MySocket
import sys
import datetime

TRITONADDR = 'TCPIP::127.0.0.1::33576::SOCKET'
LOGFOLDER = 'C:/RemoteLogging/'


def command_handler(qin, addr='TCPIP::127.0.0.1::33576::SOCKET'):
    mytriton = Triton(addr=addr)
    while True:
        nextcomm = qin.get()
        if nextcomm == 0:
            break
        qout = nextcomm[0]
        comm = nextcomm[1]
        args = nextcomm[2]
        ret = comm(mytriton, *args)
        qin.task_done()
        qout.put(ret)


if __name__ == '__main__':

    print("StLab Temperature server for Triton.  Initializing...")
    '''
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
        ff = open(filename,'a')
        ff.write('\n')
    else:
        t0 = datetime.datetime.now()
        filename = 'log_' + t0.strftime('%y_%m_%d__%H_%M_%S') + '.dat'
        varline = ['Time (s)'] + ['PT2 Head (K)','PT2 Plate (K)', 'Still Plate (K)','Cold Plate (K)','MC Cernox (K)','PT1 Head (K)','PT1 Plate (K)','MC Plate (K)'] + ['P%d (mbar)' % i for i in range(1,7)]
        #varline = ['Time (s)'] + ['T%d (K)' % i for i in range(1,10)] + ['P%d (mbar)' % i for i in range(1,7)]
        print(varline)
        ff = open(filename,'w')
        ff.write('#' + ', '.join(varline)+'\n')
    '''

    logfolder = input(
        'Enter BF log folder location (default "{}"):\n'.format(LOGFOLDER))
    if logfolder == '':
        logfolder = LOGFOLDER

    tritonaddr = input(
        'Enter address of Triton instrument (default "{}"):\n'.format(
            TRITONADDR))
    if tritonaddr == '':
        tritonaddr = TRITONADDR

    commandq = Queue(maxsize=0)

    myhandler = Thread(target=command_handler, args=(commandq, tritonaddr))
    myhandler.daemon = True
    myhandler.start()

    loggerthread = Thread(target=logger, args=(commandq, logfolder))
    loggerthread.start()

    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    #serversocket.bind((socket.gethostname(), 8001))
    #addr = socket.gethostbyname(socket.gethostname())
    addr = '0.0.0.0'  #listen on all network interfaces
    port = 8472
    serversocket.bind((addr, port))
    # become a server socket
    serversocket.listen(5)
    myip = socket.gethostbyname(socket.gethostname())
    print("Ready.  Listening on port %d and address %s" % (port, myip))

    def RunCommand(sock, resultq):
        ss = MySocket(sock)
        word = ss.myreceive()
        word = word.decode('utf_8')
        commandq.put((resultq, Triton.query, (word, )))
        xx = resultq.get()
        resultq.task_done()
        ss.mysend(xx.encode('utf_8'))
        ss.sock.close()
        return word

    resultq = Queue(maxsize=0)

    while True:
        clientsocket = None
        try:
            # accept connections from outside
            (clientsocket, address) = serversocket.accept()
            RunCommand(clientsocket, resultq)
            print("Listening on port %d and address %s" % (port, myip))
        except KeyboardInterrupt:
            print('Shutting down temperature server')
            serversocket.close()
            break

    commandq.put(0)
    loggerthread.join()
