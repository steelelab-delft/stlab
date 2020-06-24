"""He7Temperature - Driver to communicate with the custom He7 Temperature server

This driver is NOT based on a VISA instrument.  It only implements a TCP socket via the
standard socket package.  The socket implementation is in stlabutils.MySocket.
The idea is that the server script is run on the He7 control computer 
while this driver is imported in the measurement script.  The server will, upon request, 
provide the last He3 head temperature from the running log to this driver.  This is because,
typically, the BF and Entropy software blocks direct communication to the Lakeshore controller 
in order to keep the logs running.  Therefore, this driver can NOT do any write operations 
to the temperature controller or fridge.

To do write operations (like temperature control, etc.) use the BFWrapper/BFDaemon
driver/script which works for the old and new BF as well as the He7.

"""

# Basic interface to retrieve temperature measurement form BF computer
# Server must be running on BF computer (The server just checks temperature log and returns last logged value)
from stlabutils.MySocket import MySocket
from .base_instrument import base_instrument


class He7Temperature(base_instrument):
    """Class to implement temperature readout from He7 server

    A new socket is created and discarded every
    time a temperature is received.

    """

    def __init__(self,
                 addr="131.180.32.72",
                 port=8472,
                 reset=True,
                 verb=True,
                 **kwargs):
        """He7Temperature __init__ method.

        Sets up the He7 temperature socket to read from the server.

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
        if reset:
            self.reset()
        self.addr = addr
        self.port = port

    def GetTemperature(self):
        """Gets temperature from server

        Get Temperature from He7 computer (last logged value).  Returns a float in K

        Returns
        -------
        temperature : float
            The last logged He3 head temperature

        """
        '''
        create an INET, STREAMing socket
        '''
        try:
            s = MySocket(verb=self.verb)
            s.sock.connect((self.addr, self.port))
            word = s.myreceive()
            word = word.decode('utf_8')
            temperature = float(word)
            s.sock.close()
            if self.verb:
                print('He7 Temperature received: %f K' % (temperature))
        except KeyboardInterrupt:
            raise
        except:
            temperature = -1
            print('Error when reading temperature')
        return temperature

    def reset(self):
        pass

    def setverbose(self, verb=True):
        self.verb = verb

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass
