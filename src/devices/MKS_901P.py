"""Module for instance of a MKS 901p pressure gauge

This module contains the functions necessary to control a MKS 901p pressure gauge.
The system only reads and writes short byte arrays.
It does NOT inherit from instrument class.

"""
import serial
import numpy as np
import time
from stlab.devices.base_instrument import base_instrument
import io


class MKS_901P(base_instrument):
    # Constructor for IVVI Dac class.  Address is ASRLCOM1 if on COM1 serial port
    # The Serial parameters for this device are:
    # Baud = 115200, data bits = 8, parity = ODD, stop bit = 1
    # Constructor requires ndacs (integers, either 8 or 16) and polarity settings (listlike of strings, 'POS', 'NEG' or 'BIP')
    def __init__(self,
                 addr='COM4',
                 addr2=253,
                 baudrate=9600,
                 timeout=1,
                 verb=True,
                 reset=False):
        #Directly using pyserial interface and skipping pyvisa
        self.ser = serial.serial_for_url(
            addr,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        self.addr2 = addr2
        self.verb = verb
        super().__init__()

    def GetPressure(self):
        str = self.query('PR4?')
        return float(str)

    def write(self, str):
        str1 = '@{}{};FF'.format(self.addr2, str)
        if self.verb:
            print(str1)
        self.sio.write(str1)
        self.sio.flush()  # it is buffering. required to get the data out *now*
        return

    def read(self):
        result = ''
        while result[-3:] != ';FF':
            result += self.sio.read(1)
        if self.verb:
            print(result)
        result = result.strip(';FF')[7:]
        return result

    def query(self, str):
        self.write(str)
        result = self.read()
        return result

    def close(self):
        self.ser.close()
        return