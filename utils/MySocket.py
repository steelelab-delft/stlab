"""Basic socket implementation to communicate with temperature servers

Simple implementation of a python TCP socket.  Basically copied from some
example online and elaborated on.  Implements both the receiving and sending
so both the server and client use the same class.  Is used by all temperature
servers (Triton, BF, He7)

"""

import socket
import time
MSGLEN = 2048

class MySocket:
    """ Socket class

        The original comment on the example this is base on was:
        ``demonstration class only - coded for clarity, not efficiency``
    """

    def __init__(self, sock=None,verb=False,timeout=10):
        """Init method for socket

        Parameters
        ==========
        sock : socket.socket or None, optional
            If a socket has already be created it may be passed here.  If None
            then a new socket is created.
        verb : bool, optional
            Enables or disables priting of debugging strings
        timeout : float, optional
            Timeout for socket communication.  Used to avoid scripts hanging
            indefinitely waiting for a response.

        """
        self.verb = verb
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.sock.settimeout(timeout)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            #print('Sending...')
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
        try:
            while bytes_recd < MSGLEN:
                #print('Receiving...')
                chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
                print(chunk)
                if chunk == b'#EOT':
                    if self.verb:
                        print("Socket receive: Message finished")
    #                raise RuntimeError("socket connection broken")
                    return b''.join(chunks)
                elif chunk == b'':
                    print("Socket receive: Message broken?")
                    raise RuntimeError("socket connection broken")
                    return b''.join(chunks)
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            return b''.join(chunks)
        except ConnectionResetError as err:
            print(err)
            print('Connection reset, returned "None"')
            return None
        except socket.timeout as err:
            print('Receive timed out: ',err)
            return None

