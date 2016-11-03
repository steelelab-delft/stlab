from stlab.devices.triton import Triton
from queue import Queue
from threading import Thread
import time
from logger import logger
import socket
from stlab.utils.MySocket import MySocket


def command_handler(qin):
    mytriton =  Triton(verb=False)
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
    
    word = s.myreceive()
    word = word.decode('utf_8')
    
    commandq.put( (resultq, Triton.query, (word,)) )
    xx = resultq.get()
    resultq.task_done()
    
    ss.mysend(xx.encode('utf_8'))
    ss.sock.close()
    
    return word
    
resultq = Queue(maxsize=0)
    
try:
    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        RunCommand(clientsocket,resultq)
        
except KeyboardInterrupt:
    print('Shutting down temperature server')
    serversocket.close()

commandq.put(0)
loggerthread.join()