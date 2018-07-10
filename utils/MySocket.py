import socket
import time
import select
MSGLEN = 2048


class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None,verb=False,timeout=10):
        self.verb = verb
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.setblocking(0)
        self.timeout = timeout #in seconds

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            ready = select.select([], [self.sock], [], self.timeout)
            if ready[1]:
                sent = self.sock.send(msg[totalsent:])
                if sent == 0:
                    self.sock.send(b'#EOT')
                    if self.verb:
                        print("Socket send: Message finished")
    #                raise RuntimeError("socket connection broken")
                    return
            totalsent = totalsent + sent
            time.sleep(0.1)
            

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        print('In myreceive')
        try:
            tries = 0
            while bytes_recd < MSGLEN and tries<3:
                print('Check if socket ready or timeout')
                ready = select.select([self.sock], [], [], self.timeout)
                if ready[0]:
                    print('Ready. Receiving...')
                    chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
                    if chunk == b'#EOT':
                        if self.verb:
                            print("Socket receive: Message finished")
#                raise RuntimeError("socket connection broken")
                        return b''.join(chunks)
                    chunks.append(chunk)
                    bytes_recd = bytes_recd + len(chunk)
                else:
                    print('Failed, trying again...')
                    tries+=1
            return b''.join(chunks)
        except ConnectionResetError as err:
            print(err)
            print('Socket cleared, returned "None"')
            return None

