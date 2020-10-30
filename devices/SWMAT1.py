from stlab.devices.instrument import instrument


def numtostr(mystr):
    return '%12.8e' % mystr


class SWMAT1(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.127::23::SOCKET',
                 reset=True,
                 verb=True):
        super().__init__(addr, reset, verb)
        self.id()
        print(self.read())
        print(self.read())

    def GetModelName(self):
        query_str = 'MN?'
        mn = self.query(query_str)
        self.read()
        return mn
        # print(self.read())
        # if read_out is "":
        #     mn = query_out
        # else:
        #     mn = read_out
        # return mn
    
    def GetFirmware(self):
        query_str = 'FIRMWARE?'
        fmwr = self.query(query_str)
        self.read()
        return fmwr

        # if read_out is "":
        #     fmwr = query_out
        # else:
        #     fmwr = read_out
        # return fmwr

    def GetSerialNumber(self):
        query_str = 'SN?'
        serialnr = self.query(query_str)
        self.read()
        return serialnr

    def SetSwitch(self, switch_letter, switch_state):
        
        """
        Sets an individual switch whilst leaving 
        any other switches unchanged
        
        switch_letter: string; individual switch (A-D)
        
        switch_state: integer; state (1 or 2) into the switch
        should be set.
        1 == connect COM port to port 1
        2 == connect COM port to port 2

        returns 0 if command failed, 1 if command completed succesfully

        """
        self.write('SET{0}={1}'.format(switch_letter, switch_state - 1))
        read_out = self.read()
        return read_out

    def GetAllSwitchStates(self):
        """
        Returns dictionary with state values 1 or 2, of every switch, keys A-D
        and command status (0 or 1)
        
        """
        query_str = 'SWPORT?'
        query_out = self.query(query_str)
        self.read()
        temp = int(query_out)
        ss = "{0:04b}".format(temp)
        ssList = list(map(int, ss))
        ss_dic = {}
        for ii,sl in enumerate('DCBA'):
            ss_dic['Switch' + sl] = ssList[ii] + 1
        return ss_dic, command_status
        


# a Set Single SPDT / Transfer Switch SET[switch_name]=[state]
# b Set All SPDT / Transfer Switches SETP
# f Get All SPDT / Transfer Switch States SWPORT?
# j Get Model Name MN?
# k Get Serial Number SN?
# l Get Internal Temperature TEMP[sensor]?
# l Get Heat Alarm HEATALARM?
# n Get Fan Status FAN?
# o Get Firmware FIRMWARE?
# p Get SPDT / Transfer Switch Counters SC[SWITCH_NAME]?
# s Save Switch Counters SCOUNTERS:STORE:INITIATE