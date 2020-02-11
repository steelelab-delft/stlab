import socket
from stlab.utils.MySocket import MySocket
from stlab.devices.base_instrument import base_instrument


class Montana(base_instrument):
    def __init__(self,
                 addr='192.168.1.8',
                 port=7773,
                 reset=True,
                 verb=True,
                 **kwargs):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((addr, port))

    def query(self, msg):
        self.sock.send(msg.encode('ascii'))
        numlen = int(self.sock.recv(2))
        value = self.sock.recv(numlen)
        return value

    def GetTemperature(self):
        msg = self.query('03GST')
        return float(msg)

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass
