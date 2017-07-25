from stlab.devices.lakeshore import Lakeshore370
from queue import Queue
from threading import Thread
import time
#from logger import logger
import socket
from stlab.utils.MySocket import MySocket
import sys
import datetime


# Function that takes commands from queue "qin".  qin has three elements, (qout, comm, args) where qout is the output queue, comm is the function and args are the arguments for the function
# It first initializes communication to the instrument and then waits for commands to be added to the queue.  It can only run commands implemented in the BASE driver (not the wrapper)
def command_handler(qin):
    myBF =  Lakeshore370()
    while True:
        nextcomm = qin.get()
        if nextcomm == 0:
            break
        qout = nextcomm[0]
        comm = nextcomm[1]
        args = nextcomm[2]
        #print('command_handler', qout, comm, args)
        ret = comm(myBF, *args)
        #print('done')
        qin.task_done()
        qout.put(ret)

print("StLab Temperature server for BlueFors.  Initializing...")


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

#define input queue for the command handler    
commandq = Queue(maxsize=0)

#Start the thread for the command handler.  Commands added to commandq will be run and the output will be put into whatever output queue is provided in the queue element
myhandler = Thread(target=command_handler, args=(commandq,))
myhandler.daemon = True
myhandler.start()

# Another thread that also uses the same command queue
#loggerthread = Thread(target=logger, args=(commandq,))
#loggerthread.start()

# This is the main listening part of the daemon.  It is intended to listen on a specific TCP port for incoming connections.  When a connection arrives it receives 1 command that it adds to the commmandq.
# Then the connection is closed and it goes back to listening for another command.
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

#Function to add a text command received from a socket receive to the commandq.
def RunCommand(sock,resultq):
    #print('RunCommand: start')
    ss = MySocket(sock)
    word = ss.myreceive()
    word = word.decode('utf_8')
    #print('RunCommand:', word)
    if '?' in word:
        commandq.put( (resultq, Lakeshore370.query, (word,)) )
    else:
        commandq.put( (resultq, Lakeshore370.write, (word,)) )
    xx = resultq.get()
    if xx == None:
        xx = ''
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
#loggerthread.join()