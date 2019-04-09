"""Module for instance of a Rigol oscilloscope

This module contains the functions necessary to control and read data from 
a Rigol oscilloscope. The programming guide from Rigol can be found at
http://int.rigol.com/File/TechDoc/20151218/MSO1000Z&DS1000Z_ProgrammingGuide_EN.pdf
The module has been tested with a DS1054Z, but should also work with the entire
MSO1000Z/DS1000Z series.

"""

import numpy as np
from stlab.devices.instrument import instrument
import math
import time


def numtostr(mystr):
    return '%20.15e' % mystr


#    return '%20.10f' % mystr


class Rigol_DS1054(instrument):
    """Class to read and control a Rigol DS1054 scope

    Connection is done via Ethernet preferably.

    Parameters
    ----------
    addr : str, optional
        IP address of the device.  Has a default value
    reset : bool, optional
        Does nothing
    verb : bool, optional
        Enables or disables printing of status strings
        
    """

    def __init__(self,
                 addr='TCPIP::192.168.1.236::INSTR',
                 reset=True,
                 verb=True):
        """Rigol_DS1054 __init__ method.

        Sets up the connection

        """
        kwargs = {}
        kwargs['timeout'] = 10000
        super().__init__(addr, reset, verb, **kwargs)
        #self.write('STOP')

    def AutoScale(self):
        """Enables Autoscale

        """
        # autoscale
        self.write(':AUT')
        self.query('*OPC?')
        return

    def SetVoltScale(self, scal, n=1):
        """Sets the Voltage scale for a channel

        Parameters
        ----------
        scal : float
            voltage scale
        n : int, optional
            Channel number, 1 (default), 2, 3 or 4

        """
        self.write('CHAN' + str(n) + ':SCAL ' + str(scal))
        return

    def SetVoltRange(self, rang, n=1):
        """Sets the Voltage range for a channel

        Parameters
        ----------
        rang : float
            voltage range
        n : int, optional
            Channel number, 1 (default), 2, 3 or 4

        """
        self.write('CHAN' + str(n) + ':RANG ' + str(rang))
        return

    def SetTimeScale(self, scal):
        """Sets the time scale

        Parameters
        ----------
        scal : float
            time scale

        """
        self.write(':TIM:SCAL ' + str(scal))
        return

    def SetNumPoints(self, npoints):
        """Sets the number of points

        Parameters
        ----------
        npoints : float
            number of points

        """
        self.write(':ACQ:MDEPT ' + str(npoints))

    def GetSampleRate(self):
        """Gets the sample rate

        """
        return float(self.query(':ACQ:SRAT?'))

    def GetTimeScale(self):
        """Gets the time scale

        """
        return float(self.query(':TIM:SCAL?'))

    def SetMemoryDepth(self, mdep):
        """Sets the memory depth

        Parameters
        ----------
        mdep : float
            Memory depth (6e3,6e4,6e5,6e6)

        """
        self.write(':ACQ:MDEP ' + str(mdep))
        return

    def GetMemoryDepth(self):
        """Gets the memory depth

        """
        return self.query(':ACQ:MDEP?')

    def GetTrace(self, ch=1):
        """Reads what is on screen at low resolution

        Given an input channel, this function reads the data back with a resolution
        of 1200 points. Note that this is a fast operation, but you will lose quite
        a significant amount of data because the precision is range/1200

        Parameters
        ----------
        n : int
            Channel to be read out

        Returns
        -------
        (numpy.ndarray, numpy.ndarray)
            Numpy arrays of time and voltage values.

        """
        time.sleep(1)
        tscale = self.GetTimeScale()
        time.sleep(tscale * 12)
        self.write(':WAV:SOUR CHAN' + str(ch))
        self.write('WAV:MODE NORM')
        self.write('WAV:FORM BYTE')

        # xinc = float(self.query('WAV:XINC?')) # unused variable
        yinc = float(self.query('WAV:YINC?'))
        yori = float(self.query('WAV:YOR?'))
        yref = float(self.query('WAV:YREF?'))

        self.write(':WAV:DATA?')  # dat = unused variable
        output = self.dev.read_raw()
        npoints = int(output[2:11].decode('ascii'))
        print(npoints)
        output = [(x - yori - yref) * yinc for x in output[11:]]
        output = np.array(output[:npoints])
        xs = np.linspace(0, tscale * 12, len(output))
        return xs, output

    def GetMetadataString(
            self
    ):  #Should return a string of metadata adequate to write to a file
        pass

    def ReadWaveData(self, n=1, mdep=6e6):
        """Reads what is on screen at high resolution

        Given an input channel, this function reads the data back with a resolution
        limited by the memory depth and bandwidth limit. Note that this is a high
        resolution but relatively slow measurement; per channel the data retrieving 
        takes about 31 seconds.

        Parameters
        ----------
        n : int
            Channel to be read out
        mdep : float
            Memory depth [6e3|6e4|6e5|6e6]

        Returns
        -------
        numpy.ndarray
            Numpy of voltage values

        """
        self.write('STOP')
        self.write(':WAV:SOUR CHAN' + str(n))
        self.write('STOP')
        try:
            nsamp = int(self.query('ACQ:MDEP?'))
        except:
            #nsamp = input("Enter memory depth: ")
            #nsamp = int(nsamp)
            self.SetMemoryDepth(mdep)
            nsamp = int(mdep)
        self.write('WAV:MODE RAW')
        self.write('WAV:FORM BYTE')
        nmax = 250000  #Max read points 250000 when bytes
        nreads = math.ceil(nsamp / nmax)

        # to scale the data properly
        # xinc = float(self.query('WAV:XINC?')) # unused variable
        yinc = float(self.query('WAV:YINC?'))
        yori = float(self.query('WAV:YOR?'))
        yref = float(self.query('WAV:YREF?'))
        # srate = float(self.query('ACQuire:SRATe?')) # unused variable

        data = []
        for i in range(nreads):
            self.write('WAV:STAR {}'.format(i * nmax + 1))
            if i == nreads - 1:
                self.write('WAV:STOP {}'.format(nsamp))
            else:
                self.write('WAV:STOP {}'.format((i + 1) * nmax))
            self.write('WAV:DATA?')
            output = self.dev.read_raw()
            npoints = int(output[2:11].decode('ascii'))
            print(i, npoints)
            output = [(x - yori - yref) * yinc for x in output[11:]]
            output = output[:npoints]
            data.append(output)
        data = np.asarray(data).flatten()
        return data
