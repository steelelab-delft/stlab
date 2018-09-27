import socket
from stlab.utils.MySocket import MySocket
import datetime
import os.path
import os
import datetime
import glob

#LOGFOLDER = 'C:\\Entropy\\logs\\'
LOGFOLDER = 'C:\\Users\\user\\Desktop\\Entropy\\logs\\'

def GetCurrentLogFolder():
    a = next(os.walk(LOGFOLDER))[1]
    a.sort()
    a = a[::-1]
    #print(a)
    for ssa in a:
        ss = ssa.split(' ')
        if len(ss) < 2:
            continue
        else:
            try:
                print(ssa)
                dd = ss[0].split('-')
                tt = ss[1]
                din = [dd[0],dd[1],dd[2],tt[:2],tt[2:4],tt[4:6] ]
                din = [ int(b) for b in din]
                folderdate = datetime.datetime(*din)
                #print(folderdate)
                break
            except TypeError:
                continue
            except ValueError:
                continue
    return ssa        
        
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def tail( f, lines=20 ):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n'.encode())
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    blocks = [ x.decode() for x in blocks]
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])

def GetTemperature(sock):
    now = datetime.datetime.now()
    foldername = GetCurrentLogFolder()
    foldername = LOGFOLDER + foldername
    foldername = os.path.normpath(foldername)
    path = foldername + '\\*3He Head.log'
    path = glob.glob(path)
    filename = path[0]   
    myfile = open(filename,'rb')
    ss = MySocket(sock)
    word = tail(myfile,2)
    word = word.split('\t')[1]
    ss.mysend(word.encode('utf_8'))
    now = datetime.datetime.today()
    try:
        T = float(word)
    except ValueError as err:
        print(err)
        T = -1.
    print("Temperature sent at %s, T = %f K" % (now.strftime('%y-%m-%d %H:%M:%S'),T))
    ss.sock.close()

print("StLab Temperature server for He7.  Initializing...")
# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
#serversocket.bind((socket.gethostname(), 8001))
addr = socket.gethostbyname(socket.gethostname())
port = 8472
serversocket.bind(('0.0.0.0', port))
# become a server socket
serversocket.listen(5)
print("Ready.  Listening on port %d and address %s" % (port,addr))




try:
    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        GetTemperature(clientsocket)

except KeyboardInterrupt:
    print('Shutting down temperature server')
    serversocket.close()
