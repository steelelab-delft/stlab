from stlab.devices.instrument import instrument

class ThorLabsShutter(instrument):
    def __init__(self,addr='TCPIP::192.168.1.212::1470::SOCKET',verb=True):
        super(ThorLabsShutter, self).__init__(addr,reset=False,verb=verb,write_termination='\r')
        self.dev.write('')
        return
    def ToggleShutter(self):
        self.write('ens')
        return
    
