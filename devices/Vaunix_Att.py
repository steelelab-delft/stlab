"""Module for instance of a Vaunix LabBrick attenuator
This module contains the functions necessary to control and read data from 
a Vaunix LabBrick attenuator. It inherits from base_instrument.
We assume for now only one instrument connected.
A lot of this code is based on the Raytheon BBN-Q Auspex driver located
at https://github.com/BBN-Q/Auspex
"""

# from stlab.devices.base_instrument import base_instrument
import cffi
from os.path import dirname, join


class Vaunix_Att():
    def __init__(self, serial_number = None):
        '''Takes the serial number of the attenuator as an argument.
        This is only necessary if there is more than one Vaunix attenuator connected. 
        The serial number is written on a sticker under the device.
        '''

        # load API and DLL
        myffi = cffi.FFI()
        with open(
                join(dirname(__file__),
                     "Vaunix_Lab_Brick/attenuatorSDK/vnx_LDA_api_python.h")
        ) as fid:
            myffi.cdef(fid.read())

        # create device handle
        self.lib = myffi.dlopen(
            join(dirname(__file__),
                 "Vaunix_Lab_Brick/attenuatorSDK/VNX_atten64.dll"))

        # open communication
        num_devices = self.lib.fnLDA_GetNumDevices()
        dev_ids = myffi.new("unsigned int[]", [0 for i in range(num_devices)])
        self.lib.fnLDA_GetDevInfo(dev_ids)
        dev_from_serial_nums = {
            self.lib.fnLDA_GetSerialNumber(d): d
            for d in dev_ids
        }
        dev_ids = [d for d in dev_ids]

        if num_devices == 1:
            self.lib.fnLDA_SetTestMode(False)
            self.device_id = dev_from_serial_nums[list(dev_from_serial_nums)
                                                  [0]]
            status = self.lib.fnLDA_InitDevice(self.device_id)
            print('status:', status)
        elif num_devices == 0:
            raise ValueError('No devices found!')
        else:
            if serial_number is None: 
                error_str = 'Specify serial number (written under physical device)'
                error_str += ' since %d devices were detected.\n'%len(dev_ids)
                error_str+= 'The detected devices have serial numbers: '
                for num in list(dev_from_serial_nums):
                    error_str+= '%d, '%num
                raise ValueError(error_str)


            self.lib.fnLDA_SetTestMode(False)
            try:
                self.device_id = dev_from_serial_nums[serial_number]
            except KeyError:
                error_str = 'Incorrect serial number (written under physical device).\n'
                error_str+= 'The detected devices have serial numbers: '
                for num in list(dev_from_serial_nums):
                    error_str+= '%d, '%num
                raise ValueError(error_str)

            status = self.lib.fnLDA_InitDevice(self.device_id)
            print('status:', status)

        # weird conversion factors
        self.fatt = 1 / 4

        # limits
        self.max_att = self.lib.fnLDA_GetMaxAttenuation(
            self.device_id) * self.fatt
        self.min_att = self.lib.fnLDA_GetMinAttenuation(
            self.device_id) * self.fatt

        # serial number
        self.serialnumber = self.lib.fnLDA_GetSerialNumber(self.device_id)

        return

    def close(self):
        self.lib.fnLDA_CloseDevice(self.device_id)

    def CheckLimits(self, value):
        if value < self.min_att:
            print(
                'Warning: Attenuation out of range. Set to min = {} dB'.format(
                    self.min_att))
            self.SetAttenuation(self.min_att)
        elif value > self.max_att:
            print(
                'Warning: Attenuation out of range. Set to max = {} dB'.format(
                    self.max_att))
            self.SetAttenuation(self.max_att)

    def GetDeviceID(self):
        return self.device_id

    def SetAttenuation(self, att):
        self.CheckLimits(att)
        a0 = int(att / self.fatt)
        self.lib.fnLDA_SetAttenuation(self.device_id, a0)

    def GetAttenuation(self):
        a0 = float(self.lib.fnLDA_GetAttenuation(self.device_id) * self.fatt)
        return a0

    def GetMetadataString(self):
        # Should return a string of metadata adequate to write to a file
        pass