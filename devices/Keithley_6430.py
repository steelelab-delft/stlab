from stlab.devices.instrument import instrument
 
class keithley6430(instrument):
    def __init__(self,addr = "TCPIP::192.168.1.212::1470::SOCKET", reset = True, verb=True, read_termination='\r\n'):
        #Needs \r\n line termination
        super().__init__(addr,reset,verb,read_termination = read_termination)
        self.id()
    def SetOutputOn(self):
        self.write('OUTPUT ON')
        return
    def SetOutputOff(self):
        self.write('OUTPUT OFF')
        return
    def SetModeVoltage(self):
        self.write(":SOUR:FUNC VOLT")
        return
    def SetVoltage(self,volt):
        self.write(":SOUR:VOLT:LEV:IMM:AMPL {}".format(volt))
        return
    def SetComplianceCurrent(self,curr):
        self.write(":SENS:CURR:DC:PROT:LEV {}".format(curr))
        return
    def GetVoltage(self):
        result=float(self.query(":SOUR:VOLT:LEV:IMM:AMPL?"))
        return result

    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass
        
