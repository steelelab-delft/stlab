"""Module for instance of a Vaunix LabBrick Signal Generator

This module contains the functions necessary to control and read data from 
a Vaunix LabBrick Signal Generator. It inherits from base_instrument.
We assume for now only one instrument connected.
A lot of this code is based on the Raytheon BBN-Q Auspex driver located
at https://github.com/BBN-Q/Auspex
"""

# from stlab.devices.base_instrument import base_instrument
import cffi


class Vaunix_SG():
    def __init__(self, reset=True):

        # load API and DLL
        myffi = cffi.FFI()
        fid = open(
            "C:/libs/Vaunix_Lab_Brick/generatorSDK/vnx_LMS_api_python.h")
        myffi.cdef(fid.read())
        fid.close()

        # create device handle
        self.lib = myffi.dlopen(
            "C:/libs/Vaunix_Lab_Brick/generatorSDK/vnx_fmsynth.dll")

        # open communication
        num_devices = self.lib.fnLMS_GetNumDevices()
        dev_ids = myffi.new("unsigned int[]", [0 for i in range(num_devices)])
        self.lib.fnLMS_GetDevInfo(dev_ids)
        dev_from_serial_nums = {
            self.lib.fnLMS_GetSerialNumber(d): d
            for d in dev_ids
        }
        dev_ids = [d for d in dev_ids]

        if num_devices == 1:
            self.lib.fnLMS_SetTestMode(False)
            self.device_id = dev_from_serial_nums[list(dev_from_serial_nums)
                                                  [0]]
            status = self.lib.fnLMS_InitDevice(self.device_id)
            print('status:', status)
        elif num_devices == 0:
            raise ValueError('No devices found!')
        else:
            print('Warning: more than 1 device found!')

        # weird conversion factors
        self.ffreq = 10
        self.fpow = 1 / 4

        # limits
        self.max_power = self.lib.fnLMS_GetMaxPwr(self.device_id) * self.fpow
        self.min_power = self.lib.fnLMS_GetMinPwr(self.device_id) * self.fpow
        self.max_freq = self.lib.fnLMS_GetMaxFreq(self.device_id) * self.ffreq
        self.min_freq = self.lib.fnLMS_GetMinFreq(self.device_id) * self.ffreq

        # serial number
        self.serialnumber = self.lib.fnLMS_GetSerialNumber(self.device_id)

        # reset
        if reset:
            self.reset()

        return

    def reset(self):
        self.SetFrequency(self.min_freq)
        self.SetPower(self.min_power)
        self.SetReference('INT')

    def close(self):
        self.lib.fnLMS_CloseDevice(self.device_id)

    def CheckLimits(self, value, quantity):
        if (quantity == 'frequency') or (quantity == 'freq'):
            if value < self.min_freq:
                print('Warning: Frequency out of range. Set to min = {} GHz'.
                      format(self.min_freq / 1e9))
                self.SetFrequency(self.min_freq)
            elif value > self.max_freq:
                print('Warning: Frequency out of range. Set to max = {} GHz'.
                      format(self.max_freq / 1e9))
                self.SetFrequency(self.max_freq)
        elif (quantity == 'power') or (quantity == 'pow'):
            if value < self.min_power:
                print(
                    'Warning: Power out of range. Set to min = {} dBm'.format(
                        self.min_power))
                self.SetPower(self.min_power)
            elif value > self.max_power:
                print(
                    'Warning: Power out of range. Set to max = {} dBm'.format(
                        self.max_power))
                self.SetPower(self.max_power)
        else:
            raise KeyError('quantity must be either freq[ency] or pow[er]')

    def GetDeviceID(self):
        return self.device_id

    def SetRFOn(self):
        self.lib.fnLMS_SetRFOn(self.device_id, 1)

    def SetRFOff(self):
        self.lib.fnLMS_SetRFOn(self.device_id, 0)

    def SetFrequency(self, freq):
        self.CheckLimits(freq, 'freq')
        f0 = int(freq / self.ffreq)
        self.lib.fnLMS_SetFrequency(self.device_id, f0)

    def GetFrequency(self):
        f0 = float(self.lib.fnLMS_GetFrequency(self.device_id) * self.ffreq)
        return f0

    def SetPower(self, pow):
        self.CheckLimits(pow, 'pow')
        p0 = int(pow / self.fpow)
        self.lib.fnLMS_SetPowerLevel(self.device_id, p0)

    def GetPower(self):
        p0 = float(self.lib.fnLMS_GetPowerLevel(self.device_id) * self.fpow)
        return p0

    def SetReference(self, ref):
        if ref == 'INT':
            self.lib.fnLMS_SetUseInternalRef(self.device_id, 1)
        elif ref == 'EXT':
            self.lib.fnLMS_SetUseInternalRef(self.device_id, 0)
        else:
            raise ValueError('Unknown reference')

    def GetReference(self):
        msg = self.lib.fnLMS_GetUseInternalRef(self.device_id)
        if msg == 0:
            return 'EXT'
        elif msg == 1:
            return 'INT'
        else:
            raise ValueError('Unknown reference')

    def GetMetadataString(self):
        # Should return a string of metadata adequate to write to a file
        pass