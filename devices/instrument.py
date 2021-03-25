"""Module implementing instrument class

This module is at the center of the instrument control scheme.  Almost all
instrument drivers inherit from this class.  It basically repackages the basic
pyvisa write and query commands and handles the creation of the pyvisa
resource manager.  It also adds some basic reset and id commands common to
all devices that inherit from it

The class can in principle be used directly in measurement scripts but
you will be forced to explicitly write the VISA commands directly.  Most drivers
already include a collection of commands and specific quality of life methods
that allow you to already do basic functions.
"""
#import visa
import pyvisa as visa
from stlab.devices.base_instrument import base_instrument
from stlab.utils.reset_popup_warning import popup_warning


#Try to use NI-VISA
#If this fails, revert to using pyvisa-py
def makeRM():
    try:
        global_rs = visa.ResourceManager('@ivi')
        print('Global NI ResourceManager created')
        return global_rs, '@ivi' #'@ni'
    except OSError:
        return makeRMpy()


def makeRMpy():
    global_rs = visa.ResourceManager(
        '@py')  #Create resource manager using NI backend
    print('Global pyvisa-py ResourceManager created')
    return global_rs, '@py'


class instrument(base_instrument):
    """The main instrument class all visa instruments should inherit from

    Implements basic read/write/query communication for visa instruments using
    pyvisa and visa backend (usually NI-VISA).  Includes a few extra methods
    that should be common for all instruments.  Keep in mind that these methods
    can always be overridden by children of this class (for example if you always 
    need to include a wait time after querying or an ``'*OPC?'`` after writing).


    Attributes
    ----------
    global_rs : pyvisa.highlevel.ResourceManager
        Visa resource manager used to instantiate each visa instrument.
        This member is static and shared by all instrument objects
    rstype : str
        String that stores the current backend the resource manager is
        using.  Can be '@ni' or '@py' for NI-VISA or pyvisa-py backend.
    dev : pyvisa.resources.Resource
        pyvisa resource that points to the desired device.  Created
        upon instantiation.
        

    """

    global_rs = None  #Static resource manager for all instruments.  rstype is '@ni' for NI backend and '@py' for pyvisa-py
    rstype = None

    def __init__(self, addr, reset=True, verb=True, **kwargs):
        """Instrument __init__ method.

        Sets up the instrument using pyvisa and instantiates the resource
        manager if not done yet.  Upon first call it also instantiantes the
        pyvisa ResourceManager for the whole session.  It is single static member
        available to all instrument subclasses.

        Parameters
        ----------
        addr : str
            Address of the VISA instrument to be instantiated
        reset : bool, optional
            Will call :any:`reset` on instantiation to reset instrument to default settings.
            If set to False, the user will have to manually confirm three times that the reset is not wanted.
            This will happen once more if the device was instantiated using :code:`stlab.adi`
        verb : bool, optional
            Print strings written to the device on screen
        **kwargs
            Additional keyword arguments to be passed to pyvisa's open_resource method.
            See pyvisa documentation for details.  Examples could be baud_rate,
            read_termination, etc...

        """
        if not instrument.global_rs or not instrument.rstype:
            instrument.global_rs, instrument.rstype = makeRM()


#        self.rs = visa.ResourceManager('@py')
#        self.dev = self.rs.open_resource(addr)

#To correct serial resource naming depending on backend...  @py uses ASRLCOM1 and @ni uses ASRL1
        if 'ASRL' in addr:
            if self.rstype == '@py':
                if 'ASRLCOM' not in addr:
                    idx = addr.find('ASRL') + 4
                    addr = addr[:idx] + 'COM' + addr[idx:]
            if self.rstype == '@ni':
                if 'ASRLCOM' in addr:
                    idx = addr.find('ASRL') + 4
                    addr = addr[:idx] + addr[idx + 3:]

        #I have found that all our socket TCPIP devices need a \r\n line termination to work...  Add to kwargs it if not overridden
        read_termination = None
        write_termination = None

        if 'SOCKET' in addr:
            read_termination = '\n'
            write_termination = '\n'

        if 'read_termination' not in kwargs:
            kwargs['read_termination'] = read_termination

        if 'write_termination' not in kwargs:
            kwargs['write_termination'] = write_termination
        #Attempt to initialize instrument using current resource manager
        try:
            self.dev = self.global_rs.open_resource(addr, **kwargs)
        #If NI visa fails, attempt to use pyvisa-py
        except AttributeError:
            print('NI backend not working... Trying pyvisa-py')
            instrument.global_rs, instrument.rstype = makeRMpy()
            #To correct serial resource naming depending on backend...  @py uses ASRLCOM1 and @ni uses ASRL1
            if ('ASRL' in addr) and ('ASRLCOM' not in addr):
                idx = addr.find('ASRL') + 4
                addr = addr[:idx] + 'COM' + addr[idx:]
            self.dev = self.global_rs.open_resource(addr, **kwargs)
        self.verb = verb  #Whether to print commands on screen
        if not reset:
            popup = popup_warning(self.id())
            result = popup.run()
            if result:
                reset = True
                self.reset()
        else:
            self.reset()
        super().__init__()

    def write(self, mystr):
        """Write string to instrument

        Simply passes input string forward to the pyvisa resource write method

        Parameters
        ----------
        mystr : str
            The sring to write

        """
        if self.verb:
            print(mystr)
        self.dev.write(mystr)

    def query(self, mystr):
        """Write a string to instrument and read the reply

        Passes input string forward to the pyvisa resource query method and retrieves its reply

        Parameters
        ----------
        mystr
            The string to write

        Returns
        -------
        out : str
            The instrument reply string

        """
        if self.verb:
            print(mystr)
        out = self.dev.query(mystr)
        return out

    def read(self):
        """Read from the instrument

        Performs a read using the pyvisa read method

        Returns
        -------
        out : str
            The string read from the instrument

        """
        out = self.dev.read('\r')
        return out

    def id(self):
        """Query the device id string
        
        Also printed on screen.  Passes ``'*IDN?'`` to the device and prints the response.

        Returns
        -------
        out : str
            The instrument id string

        """
        out = self.query('*IDN?')
        return out

    def reset(self):
        """Send a reset command to the instrument

        Typically the reset command for VISA instruments is ``*RST``.

        """
        self.write('*RST')

    def setverbose(self, verb=True):
        """Set whether the device will print the sent commands to screen (verbosity)

        Parameters
        ----------
        verb : bool
            Set verbosity to on or off

        """
        self.verb = verb

    def close(self):
        """Closes the pyvisa resource

        """
        self.dev.close()
        if self in base_instrument.instrument_list:
            base_instrument.instrument_list.remove(
                self)  #Remove yourself from the instrument_list
        return
