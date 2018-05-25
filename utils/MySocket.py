import socket
import time
MSGLEN = 2048

class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                self.sock.send(b'#EOT')
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
                chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
                if chunk == b'#EOT':
                    print("Socket receive: Message finished")
    #                raise RuntimeError("socket connection broken")
                    return b''.join(chunks)
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
        except ConnectionResetError as err:
            print(err)
            print('Socket cleared, returned "None"')
            return None
        return b''.join(chunks)
