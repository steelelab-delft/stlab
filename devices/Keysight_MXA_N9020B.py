from stlab.devices.instrument import instrument
from stlab.utils.stlabdict import stlabdict
import logging
import numpy as np


class Keysight_MXA_N9020B(instrument):
    def __init__(self,
                 addr='TCPIP::192.168.1.164::INSTR',
                 reset=True,
                 verb=True):
        super(Keysight_MXA_N9020B, self).__init__(addr, reset, verb)
        self.dev.timeout = None

    def IQ_mode(self):
        '''
        changes to IQ mode (I am not sure what are the other options)
        '''
        return self.dev.write(':INSTrument:SELect BASIC')

    def set_center(self, f_center):
        '''
        sets center frequency for the demodulation (in Hz)
        '''
        logging.debug(__name__ + ' : Center frequency set to %d Hz' % f_center)
        return self.dev.write(':SENSe:FREQuency:CENTer %d' % f_center)

    def set_digital_IF_BW(self, IFBW=160e6):
        '''
        digital IF bandwidth (160 MHz is maximum)
        '''
        if IFBW <= 160e6:
            logging.debug(
                __name__ + ' : Digital IF bandwidth set to %d Hz ' % IFBW)
            return self.dev.write(
                ':SENSe:WAVEform:BANDwidth:RESolution %d' % IFBW)
        else:
            return 'error: Maximum IF is 160 MHz'

    def set_continuous_OFF(self):
        '''
        set to take one single measurement once the trigger line goes high
        '''
        return self.dev.write(':INIT:CONT OFF')

    def set_continuous_ON(self):
        return self.dev.write(':INIT:CONT ON')

    def set_trigger_ext1(self):
        '''
        Set the trigger to external source 1
        '''
        return self.dev.write(':TRIGger:WAVeform:SOURce EXTernal1')

    def set_trigger_positive(self):
        '''
        Set the trigger on positive edge
        '''
        return self.dev.write(':TRIGger:LINE:SLOPe POSitive')

    def set_average_OFF(self):
        return self.dev.write(':SENSe:WAVeform:AVERage OFF')

    def set_average_ON(self):
        return self.dev.write(':SENSe:WAVeform:AVERage ON')

    def set_average_type(self, x='RMS'):
        return self.dev.write(':SENSe:WAVeform:AVERage:TYPE %s' % x)

    def set_Navg(self, Navg=1):
        return self.dev.write(':SENSe:WAVeform:AVERage:Count %d' % Navg)

    def set_IQ_voltage_range_auto(self):
        '''
        Turn IQ signal ranging to auto
        '''
        return self.dev.write(':SENSe:VOLTage:IQ:RANGe:AUTO ON')

    def set_IQ_voltage_range_manual(self):
        return self.dev.write(':SENSe:VOLTage:IQ:RANGe:AUTO OFF')

    def set_data_format(self, x='ASCii'):
        '''
        Set the data format. The options are:
        'ASCii'
        'REAL,32'
        'REAL,64'
        'INT,32'
        When the numeric data format is REAL or ASCii, data is output in the current Y Axis unit. When
        the data format is INTeger, data is output in units of m dBm (.001 dBm).
        The INT,32 format returns binary 32-bit integer values in internal units (m dBm), in a definite
        length block.

        '''
        logging.debug(__name__ + ' : Data format set to %s' % x)
        return self.dev.write(':FORMat:DATA %s' % x)

    def set_sweep_time(self, t_sweep):
        '''
        Sets the sweep time
        '''
        logging.debug(__name__ + ' : sweep time set to %.9f s' % t_sweep)
        return self.dev.write(':WAVeform:SWE:TIME %.9f' % t_sweep)

    def set_attenuation(self, att=0):
        '''
        Sets the attenuation in the spectrum analyzer
        '''
        return self.dev.write(':SENSe:POWer:RF:ATTenuation %.1f' % att)

    def init_waveform(self):
        return self.dev.write(':INITiate:WAVeform')

    def measure_IQ(self):
        '''
        Measures a single IQ trace - averaging doesn't seem to work.
        Data is returned in volts.
        Here it is important to call FETCH instead of READ to avoid
        the initialization which resets the local oscillator frequency
        and therefore would randomize the phase!
        '''
        datastring = self.dev.query(':FETCH:WAV0?')
        data = np.fromstring(datastring, dtype=float, sep=',')

        I = data[0::2]
        Q = data[1::2]
        return np.array([I, Q])

    def measure_RFenvelope(self):
        '''
        Measures the RF envelope (I^2+Q^2) which seems to support
        averaging.
        Data is returned in dB.
        '''
        data_string = self.dev.query(':READ:WAV2?')

        settings_string = self.dev.query(':FETCH:WAV1?')

        powers = np.fromstring(data_string, dtype=float, sep=',')
        settings = np.fromstring(settings_string, dtype=float, sep=',')

        timestep = settings[0]
        n_samples = settings[3]

        # print('timestep %.3f' %timestep)
        # print('n_samples %.3f' %n_samples)

        times = np.arange(0, n_samples)*timestep


        data_columns = [times, powers]
        names = ['time (s)', 'power (dB)']
        final = stlabdict()

        for name, data in zip(names, data_columns):
            final[name] = data

        return final

    def set_IF_gain_LOW(self):
        return self.dev.write(':SENSe:WAV:IF:GAIN LOW')

    def set_IF_gain_HIGH(self):
        return self.dev.write(':SENSe:WAV:IF:GAIN HIGH')

    def init_waveform(self):
        return self.dev.write(':INITiate:WAVeform')
