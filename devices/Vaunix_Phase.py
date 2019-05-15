"""Module for instance of a Vaunix LabBrick phase shifter

This module contains the functions necessary to control and read data from 
a Vaunix LabBrick phase shifter. It inherits from base_instrument.
We assume for now only one instrument connected.
A lot of this code is based on the Raytheon BBN-Q Auspex driver located
at https://github.com/BBN-Q/Auspex
"""

# from stlab.devices.base_instrument import base_instrument
import cffi


class Vaunix_Phase():
    def __init__(self, reset=True):

        # load API and DLL
        myffi = cffi.FFI()
        fid = open("C:/libs/Vaunix_Lab_Brick/phaseSDK/vnx_lps_api_python.h")
        myffi.cdef(fid.read())
        fid.close()

        # create device handle
        self.lib = myffi.dlopen(
            "C:/libs/Vaunix_Lab_Brick/phaseSDK/VNX_dps64.dll")

        # open communication
        num_devices = self.lib.fnLPS_GetNumDevices()
        dev_ids = myffi.new("unsigned int[]", [0 for i in range(num_devices)])
        self.lib.fnLPS_GetDevInfo(dev_ids)
        dev_from_serial_nums = {
            self.lib.fnLPS_GetSerialNumber(d): d
            for d in dev_ids
        }
        dev_ids = [d for d in dev_ids]

        if num_devices == 1:
            self.lib.fnLPS_SetTestMode(False)
            self.device_id = dev_from_serial_nums[list(dev_from_serial_nums)
                                                  [0]]
            status = self.lib.fnLPS_InitDevice(self.device_id)
            print('status:', status)
        elif num_devices == 0:
            raise ValueError('No devices found!')
        else:
            print('Warning: more than 1 device found!')

        # weird conversion factors
        self.ffreq = 100e3  # 5.6GHz = 56000

        # limits
        self.max_freq = self.lib.fnLPS_GetMaxWorkingFrequency(
            self.device_id) * self.ffreq
        self.min_freq = self.lib.fnLPS_GetMinWorkingFrequency(
            self.device_id) * self.ffreq
        self.max_phase = self.lib.fnLPS_GetMaxPhaseShift(self.device_id)
        self.min_phase = self.lib.fnLPS_GetMinPhaseShift(self.device_id)

        # serial number
        self.serialnumber = self.lib.fnLPS_GetSerialNumber(self.device_id)

        # reset
        if reset:
            self.reset()

        return

    def reset(self):
        self.SetFrequency(self.min_freq)
        self.SetPhase(self.min_phase)

    def close(self):
        self.lib.fnLPS_CloseDevice(self.device_id)

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
        elif quantity == 'phase':
            if value < self.min_phase:
                print(
                    'Warning: Power out of range. Set to min = {} deg'.format(
                        self.min_phase))
                self.SetPhase(self.min_phase)
            elif value > self.max_phase:
                print(
                    'Warning: Power out of range. Set to max = {} deg'.format(
                        self.max_phase))
                self.SetPhase(self.max_phase)
        else:
            raise KeyError('quantity must be either freq[ency] or phase')

    def GetDeviceID(self):
        return self.device_id

    def SetFrequency(self, freq):
        self.CheckLimits(freq, 'freq')
        f0 = int(freq / self.ffreq)
        self.lib.fnLPS_SetWorkingFrequency(self.device_id, f0)

    def GetFrequency(self):
        f0 = float(
            self.lib.fnLPS_GetWorkingFrequency(self.device_id) * self.ffreq)
        return f0

    def SetPhase(self, phase):
        self.CheckLimits(phase, 'phase')
        ph0 = int(phase)
        self.lib.fnLPS_SetPhaseAngle(self.device_id, ph0)

    def GetPhase(self):
        ph0 = float(self.lib.fnLPS_GetPhaseAngle(self.device_id))
        return ph0

    def GetMetadataString(self):
        # Should return a string of metadata adequate to write to a file
        pass