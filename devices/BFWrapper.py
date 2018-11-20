"""BFWrapper - Driver to communicate with the custom BFDaemon Temperature server

This driver is NOT based on a VISA instrument.  It only implements a TCP socket via the
standard socket package.  The socket implementation is in :any:`stlab.utils.MySocket`.
The idea is that the server script is run on the fridge control computer 
while this driver is imported in the measurement script.  The server will forward any
requests from this object to the Lakeshore temperature controller and return any 
replies.

Note that a separate driver exists for the Lakeshore when directly connected to it (like
any other instrument in this package).  This wrapper, however, does not use it since it
only communicates with the BF Daemon.  The Lakeshore driver is used only on the Daemon side and
only the query method is used.

"""

from stlab.devices.base_instrument import base_instrument
from stlab.utils.MySocket import MySocket
import time

class BFWrapper(base_instrument):
    """Class to implement remote temperature readout from Lakeshore

    A new socket is created and discarded every read/write operation.

    """
    def __init__(self,addr="localhost",port=8472,reset=False,verb=True,**kwargs):
        """BFWrapper __init__ method.

        Sets up the socket to read/write from the server.

        Parameters
        ----------
        addr : str, optional
            IP address of the server.  Has a default value
        port : int, optional
            TCP port of the server.  8472 by default
        reset : bool, optional
            Does nothing
        verb : bool, optional
            Enables or disables printing of status strings
        **kwargs
            No function

        """

        self.verb = verb
    #    if reset:
    #        self.reset()
        self.addr = addr
        self.port = port
        self.htr_ranges = (0, 0.0316, 0.1, 0.316, 1., 3.16, 10., 31.6) #For heater current ranges. 0 = Off, 1 = 31.6 μA, 2 = 100 μA, 3 = 316 μA, 4 = 1.00 mA, 5 = 3.16 mA, 6 = 10.0 mA, 7 = 31.6 mA
        super().__init__()
    def query(self,mystr):
        """Query function

        Sends a VISA string (intended for the lakeshore) to the temperature to the server and retrieves a response.

        Parameters
        ----------
        mystr : str
            VISA string to send

        Returns
        -------
        word : str
            Response from server (Lakeshore)

        """
        # s = MySocket(verb=self.verb)
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
    def write(self,mystr): #All writes are queries.  If command does not contain a '?', an empty string is returned.
        """Query function

        Sends a VISA string (intended for the lakeshore) to the temperature to the server.  Sumbmitted as query
        but any reply is discarded.

        Parameters
        -------
        mystr : str
            VISA string to write

        """
        return self.query(mystr)
    #def reset(self): #I need a short pause after reset.  Otherwise the system may hang.  Not even '*OPC?' works
    #    out = self.query('*RST')
    #    time.sleep(0.1)
    def GetTemperature(self,i):
        """Get temperature from server

        Retrieves the current temperature of the desired channel

        Parameters
        -------
        i : int
            Temperature channel to read

        Returns
        -------
        float
            Temperature of channel i

        """
        if isinstance(i, int):
            if i> 6:
                print('GetTemperature: Invalid sensor')
                return -1.
        mystr = 'RDGK? {}'.format(i)
        ret = self.query(mystr)
        return float(ret)
    def SetAutorange(self,val=True):
        """Set autorange

        Enables or disables autorange on all channels

        Parameters
        -------
        val : bool
            True turns on autorange, False disables autoranging

        """
        i = 1 #Turning autorange on changes the setting for all channels.  I just use channel 1
        oldsetting = self.query('RDGRNG? {}'.format(i))
        newsetting = oldsetting.split(',')
        newsetting.insert(0,str(i))
        #I simply read the range settings from channel 1 and change the autorange element
        if val:
            newsetting[-2] = '1'
        else:
            newsetting[-2] = '0'
        newsetting = ','.join(newsetting)
        self.write('RDGRNG {}'.format(newsetting))
        return
    def SetControl(self,mode = 4):  #1 = Closed PID loop, 2 = Zone Tuning, 3 = Open Loop, 4 = off
        """Set Control mode

        Sets the control mode for the temperature loop

        Parameters
        ----------
        mode : int, optional
            Integer that determines the desired control mode.
            Possible values are:

            - 1 - Closed PID loop
            - 2 - Zone tuning
            - 3 - Open loop
            - 4 - Off

        """
        self.write('CMODE {}'.format(mode))
        return
    def SetRamp(self,mode=True,rate=0.1): #Set ramp mode and rate (in K/min).  If true, temperature set point will ramp to desired value.  If false, no ramping will be done.
        """Set Ramp mode

        When ramp is set, the temperature PID set point will ramp up to the final value instead of immediately setting the final
        desired PID value.

        Parameters
        ----------
        mode : bool, optional
            Set ramping to True or False
        rate : flaot, optional
            The desired ramp rate in K/min

        """
        rate = abs(rate)
        if mode:
            self.write('RAMP 1,{}'.format(rate))
        else:
            self.write('RAMP 0,{}'.format(rate))
    def SetHeaterValue(self,value):
        """Set Heater value

        Manually set heater value when in open loop operation.  The value is given as percentage of
        heater current range (not power).  This means that the applied power is quadratic with
        this percentage

        Parameters
        ----------
        value : bool, optional
            Percentage of current range to apply to heater

        """
        self.write('MOUT {}'.format(value))
        return
    def GetHeaterValue(self):
        """Get heater value

        Gets the current heater value as percentage of the heater current range

        Returns
        -------
        float
            Percentage of current applied to heater

        """
        return float(self.query('MOUT?'))
    def SetHeaterRange(self,range): #Specifies heater current range in mA. Will choose the minimum range to include the value given as "range"
        """Set heater current range

        Sets the maximum heater current for open or closed loop operation.  Since this
        range can only take discrete values (Off, 31.6 μA, 100 μA, 316 μA, 1.00 mA, 3.16 mA, 10.0 mA, and 31.6 mA)
        this function selects the smallest value that allows the desired range to be applied (rounds up).  If the desired value is
        above the maximum possible setting (31.6 mA), no range change will be done and a warning will be displayed (to avoid
        accidentally setting the range to maximum).

        Parameters
        ----------
        range : float
            Maximum desired value of the heater current in mA.  Will be rounded up to the nearest available setting.
            If range > 31.6 mA, the range setting will not be applied and a warning will be shown.

        """
        range = abs(range)
        rngi = -1
        for i,rr in enumerate(self.htr_ranges):
            if range <= rr:
                rngi = i
                break
        if rngi < 0:
            print('SetHeaterRange: Error, range too high.  No range change done.')
            return
        self.write('HTRRNG {}'.format(rngi))
        return
    def GetHeaterRange(self):
        """Get heater range

        Gets the maximum current that can be applied with the current range setting

        Returns
        -------
        float
            Maximum current for current range setting in mA

        """
        rr = int(self.query('HTRRNG?'))
        return(self.htr_ranges[rr])
    def SetPIDTemperature(self,value=0.):
        """Set PID temperature set point

        Changes the current set point for the closed loop PID

        Parameters
        ----------
        value : float
            Desired temperature setpoint in K

        """
        self.write('SETP {}'.format(value))
        return
    def GetSetPoint(self):
        """Get PID set point

        Gets the current temperature set point

        Returns
        -------
        float
            Current PID temperature set point in K

        """
        result = self.query('SETP?')
        result = float(result)
        return result
    def WaitForTStable(self,channel=6,tol=0.001,timeout=600.,tsettle=40.):
        """Wait for stable temperature at PID temperature
        
        Method to delay execution until temperature of given channel is considered stable at the PID set point.
        The method queries the temperature continuously until is within
        a given tolerance of the set point.  Then a settling timer is started.  If the temperature leaves
        tolerance before the settling timer is out, this timer is reset and restarted
        when the temperature is again within tolerance.  When the settling timer runs down, the execution continues
        There is also a global timeout to avoid possible infinite waiting times.

        Parameters
        ----------
        channel : int, optional
            Channel to monitor for stability. 6 by default (BF mixing chamber sensor)
        tol : float, optional
            Absolute temperature tolerance in K.  0.001 K by default
        timeout : float
            Global timeout.  The method will exit with a warning if this time is exceeded
        tsettle : float
            Settling time after reaching tolerance.  This timer is reset if the temperature
            leaves the tolerance window and restarted when the temperature is again within
            tolerance.
        
        """
        print('Stabilizing temperature...')
        Tset = self.GetSetPoint()
        t0 = time.time()
        tnow = time.time()
        tstablestart = None
        success = False
        while tnow-t0 < timeout:
            tnow = time.time()
            TT = self.GetTemperature(channel) #Get current temperature
            if abs(TT-Tset)<tol:
                if tstablestart == None:
                    tstablestart = tnow
                    print('T in tolerance.  Settling...')
            elif abs(TT-Tset)>=tol:
                if tstablestart != None:
                    print('T left tolerance')
                tstablestart = None
                continue
            if tnow-tstablestart > tsettle:
                success = True
                break
            time.sleep(0.2)
        if success:
            print("Channel " + str(channel) + " STABLE at " + str(Tset) + ' K')
        else:
            print("Channel " + str(channel) + " UNSTABLE for " + str(Tset) + ' K')
        return success

    def GetMetadataString(self):
        pass


    def SetEnableTsensor(self,ii,state=True):
        """Enable or disable temperature sensors

        Method to enable or disable given temperature sensor

        Parameters
        ----------
        ii : int
            Temperature channel to set
        state : bool
            True to enable channel, False to disable

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
