from .instrument import instrument

class ThorLabsShutter(instrument):
    def __init__(self,addr='TCPIP::192.168.1.212::1470::SOCKET',reset=True,verb=True):
        super().__init__(addr,reset=reset,verb=verb,write_termination='\r')
        self.dev.write('')
        return
    def ToggleShutter(self):
        self.write('ens')
        return
    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass
