from stlab.devices.triton import Triton
from queue import Queue
from threading import Thread
import time
from logger import logger
import socket
from stlab.utils.MySocket import MySocket
import sys
import datetime


def command_handler(qin):
    mytriton =  Triton(addr='TCPIP::127.0.0.1::33576::SOCKET')
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
    
commandq = Queue(maxsize=0)
   
myhandler = Thread(target=command_handler, args=(commandq,))
myhandler.daemon = True
myhandler.start()

loggerthread = Thread(target=logger, args=(commandq,))
loggerthread.start()

# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
#serversocket.bind((socket.gethostname(), 8001))
addr = socket.gethostbyname(socket.gethostname())
port = 8472
serversocket.bind(('', port))
# become a server socket
serversocket.listen(5)
print("Ready.  Listening on port %d and address %s" % (port,addr))

def RunCommand(sock,resultq):
    ss = MySocket(sock)
    word = ss.myreceive()
    word = word.decode('utf_8')
    commandq.put( (resultq, Triton.query, (word,)) )
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
        RunCommand(clientsocket,resultq)
    except KeyboardInterrupt:
        print('Shutting down temperature server')
        serversocket.close()
        break

commandq.put(0)
loggerthread.join()
