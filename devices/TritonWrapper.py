"""TritonWrapper - Driver to communicate with the custom Triton server

This driver is NOT based on a VISA instrument.  It only implements a TCP socket via the
standard socket package.  The socket implementation is in :any:`stlabutils.MySocket`.
The the server script is run on the fridge control computer 
while this driver is imported in the measurement script.  The server will forward any
requests from this object to the Triton fridge software and return any 
replies.

Note that a separate Triton driver exists when communication directly with the official fridge software (like
any other instrument in this package).  This wrapper, however, does not use it since it
only communicates with the Triton Daemon.  The Triton driver is used only on the Daemon side and
only the query method is used.

"""

# Basic interface to retrieve temperature measurement form Triton computer
from stlab.devices.base_instrument import base_instrument
from stlabutils.MySocket import MySocket


class TritonWrapper(base_instrument):
    """Class to implement remote control of Triton Fridge through the Triton Daemon

    A new socket is created and discarded every read/write operation.
    """
    def __init__(self,addr="131.180.82.112",port=8472,reset=False,verb=True,**kwargs):
        """init method

        Initialization of the device.
    
        Parameters
        ----------
        addr : str, optional
            IP address of the system running the Daemon (192.168.1.178) by default
        port : int, optional
            TCP port the server is listening on (8472 by default)
        reset : bool, optional
            No function
        verb : bool, optional
            Print debugging strings
        **kwargs
            No function

        """
        self.verb = verb
        if reset:
            self.reset()
        self.addr = addr
        self.port = port
    def query(self,mystr):
        """Query function

        Sends a VISA string (intended for the Triton) to the Triton Daemon and retrieves a response.

        Parameters
        ----------
        mystr : str
            VISA string to send

        Returns
        -------
        word : str
            Response from server (Triton)

        """
        s = MySocket()
        s.sock.connect((self.addr, self.port))
        if self.verb:
            print(mystr)
        s.mysend(mystr.encode('utf_8'))
        word = s.myreceive()
        word = word.decode('utf_8')
        if self.verb:
            print(word)
        s.sock.close()
        return word
    def write(self,mystr):
        """Write function

        Sends a VISA string (intended for the Triton) to the Triton Daemon.  Does not expect a response
        Given the nature of the daemon, a response is always received so all writes are
        in fact submitted as queries and the reply simply discarded.

        Returns
        -------
        word : str
            Response from server (Triton)

        """
        return self.query(mystr)
    def getpressure(self,i):
        return self.GetPressure(i)
    def GetPressure(self,i):
        """Get pressure reading

        Reads the pressure (in mbar) of the requested sensor

        Parameters
        ----------
        i : int
            Index of the requested pressure sensor

        Returns
        -------
        float
            Pressure in mbar.  -1 if invalid sensor specified.  :code:`getpressure` also works

        """
        mystr = 'READ:DEV:P%d:PRES:SIG:PRES' % i
        ret = self.query(mystr)
        ret = ret.split(':')
        ret = ret[-1]
        if ret == 'NOT_FOUND':
            print('Sensor P%d not found' % i)
            return -1.
        ret = ret.strip('mB')
        return float(ret)
    def gettemperature(self,i):
        return self.GetTemperature(i)
    def GetTemperature(self,i):
        """Get Temperature reading

        Reads the temperature (in K) of the requested sensor.  :code:`gettemperature` also works.

        Parameters
        ----------
        i : int
            Index of the requested pressure sensor

        Returns
        -------
        float
            Temperature in K.  -1 if invalid sensor specified

        """
        if i>= 10:
            print('gettemperature: Invalid sensor')
            return -1.
        mystr = 'READ:DEV:T%d:TEMP:SIG:TEMP' % i
        ret = self.query(mystr)
        ret = ret.split(':')
        ret = ret[-1]
        if ret == 'NOT_FOUND':
            print('Sensor P%d not found' % i)
            return -1.
        ret = ret.strip('K')
        return float(ret)
    def SetMCHeater(self,xx):
        """Set mixing chamber heater power

        Set the mixing chamber heater power (in uW?) to given value

        Parameters
        ----------
        xx : float
            Desired heater power

        """
        mystr = 'SET:DEV:H1:HTR:SIG:POWR:{}'.format(xx)
        reply = self.query(mystr)
        print(reply[reply.rfind(":"):])
        return
    def SetStillHeater(self,xx):
        """Set still heater power

        Set the still heater power (in uW?) to given value

        Parameters
        ----------
        xx : float
            Desired heater power

        """
        mystr = 'SET:DEV:H2:HTR:SIG:POWR:%f' % xx
        reply = self.query(mystr)
        print(reply[reply.rfind(":")+1:])
        return
    def SetEnableTsensor(self,ii,state=True):
        """Enable/Disable temperature sensors

        Enables or disables the requested temperature sensor

        Parameters
        ----------
        ii : int
            Index of temperature sensor
        state : bool, optional
            True enables the sensor and False disables it

        """
        if ii>= 10:
            print('SetEnableTsensor: Invalid sensor ',ii)
            return -1.
        if state:
            mystr = 'SET:DEV:T%d:TEMP:MEAS:ENAB:ON' % ii
        elif not state:
            mystr = 'SET:DEV:T%d:TEMP:MEAS:ENAB:OFF' % ii
        reply = self.query(mystr)
        return
    def GetTurbo(self):
        """ Get turbo status string

        Returns turbo values in order Power, Speed, PST, MT, BT, PBT, ET (temperatures... whatever they mean...)

        Returns
        -------
        result : list of float
            Array containing current values of Turbo parameters [Power, Speed, PST, MT, BT, PBT, ET]

        """
        result = []
        
        mystr = self.query('READ:DEV:TURB1:PUMP:SIG:POWR')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('W')
        result.append(float(mystr))
        
        mystr = self.query('READ:DEV:TURB1:PUMP:SIG:SPD')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('Hz')
        result.append(float(mystr))
        
        temps = ['PST','MT','BT','PBT','ET']
        for ss in temps:
            mystr = self.query('READ:DEV:TURB1:PUMP:SIG:{}'.format(ss))
            mystr = mystr.split(':')[-1]
            mystr = mystr.strip('C')
            result.append(float(mystr))
        return result
    def reset(self): #No reset for the triton
        pass
    def SetVerbose(self,verb=True):
        """Change verbosity

        Enables/disables printing of debugging strings

        Parameters
        ----------
        verb : bool, optional
            True enables debugging strings, False disables them.

        """
        self.verb = verb
    def SetPID(self,val = True):
        """Enables or disables the mixing chamber PID loop

        Parameters
        ----------
        val : bool, optional
            True enables the PID loop, False disables it

        """
        if val:
            self.write('SET:DEV:T8:TEMP:LOOP:MODE:ON')
        else:
            self.write('SET:DEV:T8:TEMP:LOOP:MODE:OFF')
        return
    def SetHeaterRange(self,val):  #Value is in mA
        """Set mixing chamber heater range

        Sets the range for the mixing chamber heater (for temperature control and PID)

        Parameters
        ----------
        val : float
            Desired range value (in mA).

        """
        self.write('SET:DEV:T8:TEMP:LOOP:RANGE:{}'.format(val))
        return
    def SetPIDTemperature(self,val=0.):
        """Set the mixing chamber temperature set point

        Adjusts the desired mixing chamber temperature for the PID loop

        Parameters
        ----------
        val : float, optional
            New temperature setpoint

        """
        self.write('SET:DEV:T8:TEMP:LOOP:TSET:{}'.format(val))
        return

    def GetPTC(self): #Returns PTC values in order WIN, WOT, OILT, HT, HLP, HHP, MCUR, HRS
        """ Get compressor status string

        Returns compressor values in order WIN, WOT, OILT, HT, HLP, HHP, MCUR, HRS (whatever the abbreviations mean...)

        Returns
        -------
        result : list of float
            Array containing current values of compressor and pulse tube parameters [WIN, WOT, OILT, HT, HLP, HHP, MCUR, HRS]

        """
        result = []
 
        temps = ['WIT','WOT','OILT','HT']
        for ss in temps:
            mystr = self.query('READ:DEV:C1:PTC:SIG:{}'.format(ss))
            mystr = mystr.split(':')[-1]
            mystr = mystr.strip('C')
            result.append(float(mystr))

        mystr = self.query('READ:DEV:C1:PTC:SIG:HLP')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('B')
        result.append(float(mystr))
        
        mystr = self.query('READ:DEV:C1:PTC:SIG:HHP')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('B')
        result.append(float(mystr))

        mystr = self.query('READ:DEV:C1:PTC:SIG:MCUR')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('A')
        result.append(float(mystr))

        mystr = self.query('READ:DEV:C1:PTC:SIG:HRS')
        mystr = mystr.split(':')[-1]
        mystr = mystr.strip('h')
        result.append(float(mystr))
        return result
        
    def SetPTOn(self):
        """Turn on compressor/pulse tube cooler

        Starts the compressor

        """
        self.write('SET:DEV:C1:PTC:SIG:STATE:ON')
        return
    def SetPTOff(self):
        """Turn of compressor/pulse tube cooler

        Stops the compressor

        """
        self.write('SET:DEV:C1:PTC:SIG:STATE:OFF')
        return
    def GetMetadataString(self):
        pass

