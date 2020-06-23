import socket
from stlabutils.MySocket import MySocket
from stlab.devices.base_instrument import base_instrument

class montana(base_instrument):
    def __init__(self,addr='192.168.1.8',port=7773,reset=True,verb=True,**kwargs):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((addr,port))
    def query(self,msg):
        self.sock.send(msg.encode('ascii'))
        numlen = int(self.sock.recv(2))
        value = self.sock.recv(numlen)
        return value
    def gettemperature(self):
        msg = self.query('03GST')
        return float(msg)
    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass



'''

instr = rm.open_resource('TCPIP::192.168.1.212::1470::SOCKET',read_termination='\r',write_termination='\r')
instr.write('mode=1')
instr.write('ens')
time.sleep(0.5)
instr.write('ens')
time.sleep(0.5)
instr.write('ens')
time.sleep(0.5)
instr.write('ens')
time.sleep(0.5)
'''


'''
'''

'''
pna = pnaclass(reset=True)
data = pna.Measure2ports()
print(data)
'''


'''
pna.SetContinuous(False)

pna.ClearAll()
print(pna.query('CALC:PAR:CAT?'))

tracenames = ['\'TrS11\'','\'TrS21\'']
tracevars = ['\'S11\'','\'S21\'']
windows = ['1','2']
first = True
for name,var,wind in zip(tracenames,tracevars,windows):
    pna.write('DISP:WIND'+wind+':STAT ON')
    pna.write('CALC:PAR:SDEF ' + name + ', ' + var) #Set 2 traces and measurements
    pna.write('DISP:WIND'+wind+':TRAC:FEED ' + name)
pna.write("CALC:PAR:DEL 'Trc1'")
print(pna.query('CALC:PAR:CAT?'))
pna.ClearAll()
print(pna.query('CALC:PAR:CAT?'))
time.sleep(5)
'''

