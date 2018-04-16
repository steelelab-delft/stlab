# Tektronix_AWG520.py class, to perform the communication between the Wrapper and the device
# Pieter de Groot <pieterdegroot@gmail.com>, 2008
# Martijn Schaafsma <qtlab@mcschaafsma.nl>, 2008
# Vishal Ranjan, 2012
# ron schutjens, 2012
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from stlab.devices.instrument import instrument
import types
import time
import logging
import numpy as np
import struct

class Tektronix_AWG520(instrument):
    '''
    This is the python driver for the Tektronix AWG520
    Arbitrary Waveform Generator
    Usage:
    Initialize with
    <name> = instruments.create('name', 'Tektronix_AWG520', address='<GPIB address>',
        reset=<bool>, numpoints=<int>)
    think about:    clock, waveform length
    TODO:
    1) Get All
    2) Remove test_send??
    3) Add docstrings
    '''

    def __init__(self, addr='TCPIP::192.168.1.27::1234::SOCKET', reset=False, verb=False, numpoints=1000,**kw):
        '''
        Initializes the AWG520.
        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            reset (bool)     : resets to default values, default=false
            numpoints (int)  : sets the number of datapoints
        Output:
            None
        '''
        logging.debug(__name__ + ' : Initializing instrument')
        super().__init__(addr, reset, verb, read_termination = '\n')

        self._values = {}
        self._values['files'] = {}
       
        self._numpoints = numpoints
        self._fname = ''

      

        if reset:
            self.reset()
        if self.verb:
            self.get_all()

 

    #get state AWG
    def get_state(self):
        state=int(self.query('AWGC:RSTATE?'))
        if state == 0:
            return 'Idle'
        elif state == 1:
            return 'Waiting for trigger'
        elif state == 2:
            return 'Running'

        else:
            logging.error(__name__  + ' : AWG in undefined state')
            return 'error'
       

    def start(self):
        self.write('AWGC:RUN')
        return self.get_state()

    def stop(self):
        self.write('AWGC:STOP')



    def get_folder_contents(self):
        return self.query('mmem:cat?')

    def get_current_folder_name(self):
        return self.query('mmem:cdir?')

    def set_current_folder_name(self,file_path):
        self.write('mmem:cdir "%s"'%file_path)

    def change_folder(self,dir):
        self.write('mmem:cdir "%s"' %dir)

    def goto_root(self):
        self.write('mmem:cdir')

    def make_directory(self,dir,root):
        '''
        makes a directory
        if root = True, new dir in main folder
        '''
        if root == True:
            self.goto_root()
            self.write('MMEMory:MDIRectory "%s"' %dir)
        else:
            self.write('MMEMory:MDIRectory "%s"' %dir)




    def get_all(self):
        '''
        Reads all implemented parameters from the instrument,
        and updates the wrapper.
        Input:
            None
        Output:
            None
        '''
        
        logging.info(__name__ + ' : Reading all data from instrument')

        print ('Instrument State: ',self.get_state())
        print ('Mode:', self.get_trigger_mode())
        print ('Trigger impedance (Ohm):', self.get_trigger_impedance())
        print ('Trigger level (V): ' , self.get_trigger_level())
        print ('Number of points: ' , self.get_numpoints())
        print ('Sample rate (Hz): ', self.get_clock())
        print ('Reference Oscillator: ', self.get_refclock())



        for i in range(1,3):
            print ('Amplitude Channel{} (V): '.format(i), self.get_amplitude(i))
            print ('Offset Channel{} (V):'.format(i), self.get_offset(i))
            print ('Channel{} Marker1_low (V)'.format(i), self.get_marker1_low(i))
            print ('Channel{} Marker1_high (V)'.format(i), self.get_marker1_high(i))
            print ('Channel{} Marker2_low (V)'.format(i), self.get_marker2_low(i))
            print ('Channel{} Marker2_high (V)'.format(i), self.get_marker2_high(i))
            print ('Channel{} state: '.format(i), self.get_status(i))
        


    def clear_waveforms(self):
        '''
        Clears the waveform on both channels.
        Input:
            None
        Output:
            None
        '''
        logging.debug(__name__ + ' : Clear waveforms from channels')
        self.write('SOUR1:FUNC:USER ""')
        self.write('SOUR2:FUNC:USER ""')

    def set_trigger_mode_on(self):
        '''
        Sets the trigger mode to 'On'
        Input:
            None
        Output:
            None
        '''
        logging.debug(__name__  +' : Set trigger mode tot TRIG')
        self.write('AWGC:RMOD TRIG')

    def set_trigger_mode_off(self):
        '''
        Sets the trigger mode to 'Cont'
        Input:
            None
        Output:
            None
        '''
        logging.debug(__name__  +' : Set trigger mode to CONT')
        self.write('AWGC:RMOD CONT')

    def set_trigger_impedance_1e3(self):
        '''
        Sets the trigger impedance to 1 kOhm
        Input:
            None
        Output:
            None
        '''
        logging.debug(__name__  + ' : Set trigger impedance to 1e3 Ohm')
        self.write('TRIG:IMP 1e3')

    def set_trigger_impedance_50(self):
        '''
        Sets the trigger impedance to 50 Ohm
        Input:
            None
        Output:
            None
        '''
        logging.debug(__name__  + ' : Set trigger impedance to 50 Ohm')
        self.write('TRIG:IMP 50')

    # Parameters
    def get_trigger_mode(self):
        '''
        Reads the trigger mode from the instrument
        Input:
            None
        Output:
            mode (string) : 'Trig' or 'Cont' depending on the mode
        '''
        logging.debug(__name__  + ' : Get trigger mode from instrument')
        return self.query('AWGC:RMOD?')

    def set_trigger_mode(self, mod):
        '''
        Sets trigger mode of the instrument
        Input:
            mod (string) : Either 'Trig' or 'Cont' depending on the mode
        Output:
            None
        '''
        if (mod.upper()=='TRIG'):
            self.set_trigger_mode_on()
        elif (mod.upper()=='CONT'):
            self.set_trigger_mode_off()
        else:
            logging.error(__name__ + ' : Unable to set trigger mode to %s, expected "TRIG" or "CONT"' %mod)

    def get_trigger_impedance(self):
        '''
        Reads the trigger impedance from the instrument
        Input:
            None
        Output:
            impedance (??) : 1e3 or 50 depending on the mode
        '''
        logging.debug(__name__  + ' : Get trigger impedance from instrument')
        return self.query('TRIG:IMP?')

    def set_trigger_impedance(self, mod):
        '''
        Sets the trigger impedance of the instrument
        Input:
            mod (int) : Either 1e3 of 50 depending on the mode
        Output:
            None
        '''
        if (mod==1e3):
            self.set_trigger_impedance_1e3()
        elif (mod==50):
            self.set_trigger_impedance_50()
        else:
            logging.error(__name__ + ' : Unable to set trigger impedance to %s, expected "1e3" or "50"' %mod)

    def get_trigger_level(self):
        '''
        Reads the trigger level from the instrument
        Input:
            None
        Output:
            None
        '''
        logging.debug(__name__  + ' : Get trigger level from instrument')
        return float(self.query('TRIG:LEV?'))

    def set_trigger_level(self, level):
        '''
        Sets the trigger level of the instrument
        Input:
            level (float) : trigger level in volts
        '''
        logging.debug(__name__  + ' : Trigger level set to %.3f' %level)
        self.write('TRIG:LEV %.3f' %level)

    def force_trigger(self):
        '''
        forces a trigger event (used for wait_trigger option in sequences)
        Ron
        '''
        return self.write('TRIG:SEQ:IMM')

    def force_logicjump(self):
        '''
        forces a jumplogic event (used as a conditional event during waveform
        executions)
        note: jump_logic events&mode have to be set properly!
        Ron
        '''
        return self.write('AWGC:EVEN:SEQ:IMM')

    def set_run_mode(self,mode):
        '''
        sets the run mode of the AWG.
        mode can be: CONTinuous,TRIGgered,GATed,ENHanced
        Ron
        '''
        return self.write('AWGC:RMOD %s' %mode)

    def get_run_mode(self):
        '''
        sets the run mode of the AWG
        Ron
        '''
        return self.query('AWGC:RMOD?')

    def set_jumpmode(self,mode):
        '''
        sets the jump mode for jump logic events, possibilities:
        LOGic,TABle,SOFTware
        give mode as string
        note: jump_logic events&mode have to be set properly!
        Ron
        '''
        return self.write('AWGC:ENH:SEQ:JMOD %s' %mode)

    def get_jumpmode(self,mode):
        '''
        get the jump mode for jump logic events
        Ron
        '''
        return self.query('AWGC:ENH:SEQ:JMOD?')


    def get_numpoints(self):
        '''
        Returns the number of datapoints in each wave
        Input:
            None
        Output:
            numpoints (int) : Number of datapoints in each wave
        '''
        return self._numpoints

    def set_numpoints(self, numpts):
        '''
        Sets the number of datapoints in each wave.
        This acts on both channels.
        Input:
            numpts (int) : The number of datapoints in each wave
        Output:
            None
        '''
        logging.debug(__name__ + ' : Trying to set numpoints to %s' %numpts)
        if numpts != self._numpoints:
            logging.warning(__name__ + ' : changing numpoints. This will clear all waveforms!')

        response = 'yes'#raw_input('type "yes" to continue')
        if response is 'yes':
            logging.debug(__name__ + ' : Setting numpoints to %s' %numpts)
            self._numpoints = numpts
            self.clear_waveforms()
        else:
            print ('aborted')

    def get_clock(self):
        '''
        Returns the clockfrequency, which is the rate at which the datapoints are
        sent to the designated output
        Input:
            None
        Output:
            clock (int) : frequency in Hz
        '''
        return self.query('SOUR:FREQ?')

    def set_clock(self, clock):
        '''
        Sets the rate at which the datapoints are sent to the designated output channel
        Input:
            clock (int) : frequency in Hz
        Output:
            None
        '''
        logging.warning(__name__ + ' : Clock set to %s. This is not fully functional yet. To avoid problems, it is better not to change the clock during operation' % clock)
        self._clock = clock
        self.write('SOUR:FREQ %f' % clock)

    def get_refclock(self):
        '''
        Asks AWG whether the 10 MHz reference is set to the
        internal source or an external one.
        Input:
            None
        Output:
            'INT' or 'EXT'
        '''
        return self.query('SOUR1:ROSC:SOUR?')

    def set_refclock_ext(self):
        '''
        Sets the reference clock to internal or external.
        '''
        self.write('SOUR1:ROSC:SOUR EXT')

    def set_refclock_int(self):
        '''
        Sets the reference clock to internal or external
        '''
        self.write('SOUR1:ROSC:SOUR INT')


    def get_amplitude(self, channel):
        '''
        Reads the amplitude of the designated channel from the instrument
        Input:
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            amplitude (float) : the amplitude of the signal in Volts
        '''
        logging.debug(__name__ + ' : Get amplitude of channel %s from instrument'
            %channel)
        return float(self.query('SOUR%s:VOLT:LEV:IMM:AMPL?' % channel))

    def set_amplitude(self, amp, channel):
        '''
        Sets the amplitude of the designated channel of the instrument
        Input:
            amp (float)   : amplitude in Volts
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            None
        '''
        logging.debug(__name__ + ' : Set amplitude of channel %s to %.6f'
            %(channel, amp))
        self.write('SOUR%s:VOLT:LEV:IMM:AMPL %.6f' % (channel, amp))

    def get_offset(self, channel):
        '''
        Reads the offset of the designated channel of the instrument
        Input:
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            offset (float) : offset of designated channel in Volts
        '''
        logging.debug(__name__ + ' : Get offset of channel %s' %channel)
        return float(self.query('SOUR%s:VOLT:LEV:IMM:OFFS?' % channel))

    def set_offset(self, offset, channel):
        '''
        Sets the offset of the designated channel of the instrument
        Input:
            offset (float) : offset in Volts
            channel (int)  : 1 or 2, the number of the designated channel
        Output:
            None
        '''
        logging.debug(__name__ + ' : Set offset of channel %s to %.6f' %(channel, offset))
        self.write('SOUR%s:VOLT:LEV:IMM:OFFS %.6f' % (channel, offset))

    def get_marker1_low(self, channel):
        '''
        Gets the low level for marker1 on the designated channel.
        Input:
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            low (float) : low level in Volts
        '''
        logging.debug(__name__ + ' : Get lower bound of marker1 of channel %s' %channel)
        return float(self.query('SOUR%s:MARK1:VOLT:LEV:IMM:LOW?' % channel))

    def set_marker1_low(self, low, channel):
        '''
        Sets the low level for marker1 on the designated channel.
        Input:
            low (float)   : low level in Volts
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            None
         '''
        logging.debug(__name__ + ' : Set lower bound of marker1 of channel %s to %.3f'
            %(channel, low))
        self.write('SOUR%s:MARK1:VOLT:LEV:IMM:LOW %.3f' % (channel, low))

    def get_marker1_high(self, channel):
        '''
        Gets the high level for marker1 on the designated channel.
        Input:
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            high (float) : high level in Volts
        '''
        logging.debug(__name__ + ' : Get upper bound of marker1 of channel %s' %channel)
        return float(self.query('SOUR%s:MARK1:VOLT:LEV:IMM:HIGH?' % channel))

    def set_marker1_high(self, high, channel):
        '''
        Sets the high level for marker1 on the designated channel.
        Input:
            high (float)   : high level in Volts
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            None
         '''
        logging.debug(__name__ + ' : Set upper bound of marker1 of channel %s to %.3f'
            %(channel,high))
        self.write('SOUR%s:MARK1:VOLT:LEV:IMM:HIGH %.3f' % (channel, high))

    def get_marker2_low(self, channel):
        '''
        Gets the low level for marker2 on the designated channel.
        Input:
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            low (float) : low level in Volts
        '''
        logging.debug(__name__ + ' : Get lower bound of marker2 of channel %s' %channel)
        return float(self.query('SOUR%s:MARK2:VOLT:LEV:IMM:LOW?' % channel))

    def set_marker2_low(self, low, channel):
        '''
        Sets the low level for marker2 on the designated channel.
        Input:
            low (float)   : low level in Volts
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            None
         '''
        logging.debug(__name__ + ' : Set lower bound of marker2 of channel %s to %.3f'
            %(channel, low))
        self.write('SOUR%s:MARK2:VOLT:LEV:IMM:LOW %.3f' % (channel, low))

    def get_marker2_high(self, channel):
        '''
        Gets the high level for marker2 on the designated channel.
        Input:
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            high (float) : high level in Volts
        '''
        logging.debug(__name__ + ' : Get upper bound of marker2 of channel %s' %channel)
        return float(self.query('SOUR%s:MARK2:VOLT:LEV:IMM:HIGH?' % channel))

    def set_marker2_high(self, high, channel):
        '''
        Sets the high level for marker2 on the designated channel.
        Input:
            high (float)   : high level in Volts
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            None
         '''
        logging.debug(__name__ + ' : Set upper bound of marker2 of channel %s to %.3f'
            %(channel,high))
        self.write('SOUR%s:MARK2:VOLT:LEV:IMM:HIGH %.3f' % (channel, high))

    def get_status(self, channel):
        '''
        Gets the status of the designated channel.
        Input:
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            None
        '''
        logging.debug(__name__ + ' : Get status of channel %s' %channel)
        outp = int(self.query('OUTP%s?' %channel))
        if (outp==0):
            return 'off'
        elif (outp==1):
            return 'on'
        else:
            logging.debug(__name__ + ' : Read invalid status from instrument %s' %outp)
            return 'an error occurred while reading status from instrument'

    def set_status(self, status, channel):
        '''
        Sets the status of designated channel.
        Input:
            status (string) : 'On' or 'Off'
            channel (int)   : channel number
        Output:
            None
        '''
        logging.debug(__name__ + ' : Set status of channel %s to %s'
            %(channel, status))
        if (status.upper()=='ON'):
            self.write('OUTP%s ON' %channel)
        elif (status.upper()=='OFF'):
            self.write('OUTP%s OFF' %channel)
        else:
            logging.debug(__name__ + ' : Try to set status to invalid value %s' % status)
            print ('Tried to set status to invalid value %s' %status)

    #  query for string with filenames
    def get_filenames(self):
        logging.debug(__name__ + ' : Read filenames from instrument')
        return self.query('MMEM:CAT? "MAIN"')

  
    def set_setup_filename(self, fname, force_load=False):
        if self._fname == fname and not force_load:
            print ('File %s already loaded in AWG520' %fname)
            return
        else:
            self._fname = fname
            filename = "\%s/%s.seq" % (fname, fname)
            self.set_sequence(filename=filename)
            print ('Waiting for AWG to load file "%s"' % fname)
            sleeptime = 0.5
            # while state idle is not possible due to timeout error while loading
            t0 = time.time()
            while(time.time()-t0 < 360):
                try:
                    if self.get_state() == 'Idle':
                        break
                except:
                    time.sleep(sleeptime)
                    print ('.')
            self.get_state()
            print ('Loading file took %.2fs' % (time.time()-t0))
            return

    def set_sequence(self,filename):
        '''
        loads a sequence file on all channels.
        Waveforms/patterns to be executed on respective channel
        must be defined inside the sequence file itself
        make sure to send all waveforms before setting a seq
        '''
        self.write('SOUR%s:FUNC:USER "%s","MAIN"' % (1, filename))


    def do_set_filename(self, name, channel):
        '''
        Specifies which file has to be set on which channel
        Make sure the file exists, and the numpoints and clock of the file
        matches the instrument settings.
        If file doesn't exist an error is raised, if the numpoints doesn't match
        the command is neglected
        Input:
            name (string) : filename of uploaded file
            channel (int) : 1 or 2, the number of the designated channel
        Output:
            None
        '''
        logging.debug(__name__  + ' : Try to set %s on channel %s' %(name, channel))
        exists = False
        if name in self._values['files']:
            exists= True
            logging.debug(__name__  + ' : File exists in local memory')
            self._values['recent_channel_%s' %channel] = self._values['files'][name]
            self._values['recent_channel_%s' %channel]['filename'] = name
        else:
            logging.debug(__name__  + ' : File does not exist in memory, \
            reading from instrument')
            lijst = self.query('MMEM:CAT? "MAIN"')
            bool = False
            bestand=""
            for i in range(len(lijst)):
                if (lijst[i]=='"'):
                    bool=True
                elif (lijst[i]==','):
                    bool=False
                    if (bestand==name): exists=True
                    bestand=""
                elif bool:
                    bestand = bestand + lijst[i]
        if exists:
            data = self.query('MMEM:DATA? "%s"' %name)
            logging.debug(__name__  + ' : File exists on instrument, loading \
            into local memory')
            # string alsvolgt opgebouwd: '#' <lenlen1> <len> 'MAGIC 1000\r\n' '#' <len waveform> 'CLOCK ' <clockvalue>
            len1=int(data[1])
            len2=int(data[2:2+len1])
            i=len1
            tekst = ""
            while (tekst!='#'):
                tekst=data[i]
                i=i+1
            len3=int(data[i])
            len4=int(data[i+1:i+1+len3])

            w=[]
            m1=[]
            m2=[]

            for q in range(i+1+len3, i+1+len3+len4,5):
                j=int(q)
                c,d = struct.unpack('<fB', data[j:5+j])
                w.append(c)
                m2.append(int(d/2))
                m1.append(d-2*int(d/2))

            clock = float(data[i+1+len3+len4+5:len(data)])

            self._values['files'][name]={}
            self._values['files'][name]['w']=w
            self._values['files'][name]['m1']=m1
            self._values['files'][name]['m2']=m2
            self._values['files'][name]['clock']=clock
            self._values['files'][name]['numpoints']=len(w)

            self._values['recent_channel_%s' %channel] = self._values['files'][name]
            self._values['recent_channel_%s' %channel]['filename'] = name
        else:
            logging.error(__name__  + ' : Invalid filename specified %s' %name)

        if (self._numpoints==self._values['files'][name]['numpoints']):
            logging.debug(__name__  + ' : Set file %s on channel %s' % (name, channel))
            self.write('SOUR%s:FUNC:USER "%s","MAIN"' % (channel, name))
        else:
            self.write('SOUR%s:FUNC:USER "%s","MAIN"' % (channel, name))
            logging.warning(__name__  + ' : Verkeerde lengte %s ipv %s'
                %(self._values['files'][name]['numpoints'], self._numpoints))




    # Send waveform to the device
    def send_waveform(self,w,m1,m2,filename,clock):
        '''
        Sends a complete waveform. All parameters need to be specified.
        choose a file extension 'wfm' (must end with .pat)
        See also: resend_waveform()
        Input:
            w (float[numpoints]) : waveform
            m1 (int[numpoints])  : marker1
            m2 (int[numpoints])  : marker2
            filename (string)    : filename
            clock (int)          : frequency (Hz)
        Output:
            None
        '''
        logging.debug(__name__ + ' : Sending waveform %s to instrument' % filename)

        # Check for errors
        dim = len(w)

        if (not((len(w)==len(m1)) and ((len(m1)==len(m2))))):
            return 'error'
        self._values['files'][filename]={}
        self._values['files'][filename]['w']=w
        self._values['files'][filename]['m1']=m1
        self._values['files'][filename]['m2']=m2
        self._values['files'][filename]['clock']=clock
        self._values['files'][filename]['numpoints']=len(w)

        m = m1 + np.multiply(m2,2)
        ws = ''
        for i in range(0,len(w)):
            ws = ws + struct.pack('<fB', w[i], int(m[i]))


        s1 = 'MMEM:DATA "%s",' % filename
        s3 = 'MAGIC 1000\n'
        s5 = ws
        s6 = 'CLOCK %.10e\n' % clock

        s4 = '#' + str(len(str(len(s5)))) + str(len(s5))
        lenlen=str(len(str(len(s6) + len(s5) + len(s4) + len(s3))))
        s2 = '#' + lenlen + str(len(s6) + len(s5) + len(s4) + len(s3))

        mes = s1 + s2 + s3 + s4 + s5 + s6
        self.write(mes)

    def send_pattern(self,w,m1,m2,filename,clock):
        '''
        Sends a pattern file.
        similar to waveform except diff file extension
        number of points different. diff byte conversion
        See also: resend_waveform()
        Input:
            w (float[numpoints]) : waveform
            m1 (int[numpoints])  : marker1
            m2 (int[numpoints])  : marker2
            filename (string)    : filename
            clock (int)          : frequency (Hz)
        Output:
            None
        '''
        logging.debug(__name__ + ' : Sending pattern %s to instrument' % filename)

        # Check for errors
        dim = len(w)

        if (not((len(w)==len(m1)) and ((len(m1)==len(m2))))):
            return 'error'
        self._values['files'][filename]={}
        self._values['files'][filename]['w']=w
        self._values['files'][filename]['m1']=m1
        self._values['files'][filename]['m2']=m2
        self._values['files'][filename]['clock']=clock
        self._values['files'][filename]['numpoints']=len(w)

        m = m1 + np.multiply(m2,2)
        ws = ''
        for i in range(0,len(w)):
            ws = ws + struct.pack('<fB', w[i], int(m[i]))

        s1 = 'MMEM:DATA "%s",' % filename
        s3 = 'MAGIC 2000\n'
        s5 = ws
        s6 = 'CLOCK %.10e\n' % clock

        s4 = '#' + str(len(str(len(s5)))) + str(len(s5))
        lenlen=str(len(str(len(s6) + len(s5) + len(s4) + len(s3))))
        s2 = '#' + lenlen + str(len(s6) + len(s5) + len(s4) + len(s3))

        mes = s1 + s2 + s3 + s4 + s5 + s6
        self.write(mes)


    def resend_waveform(self, channel, w=[], m1=[], m2=[], clock=[]):
        '''
        Resends the last sent waveform for the designated channel
        Overwrites only the parameters specifiedta
        Input: (mandatory)
            channel (int) : 1 or 2, the number of the designated channel
        Input: (optional)
            w (float[numpoints]) : waveform
            m1 (int[numpoints])  : marker1
            m2 (int[numpoints])  : marker2
            clock (int) : frequency
        Output:
            None
        '''
        filename = self._values['recent_channel_%s' %channel]['filename']
        logging.debug(__name__ + ' : Resending %s to channel %s' % (filename, channel))


        if (w==[]):
            w = self._values['recent_channel_%s' %channel]['w']
        if (m1==[]):
            m1 = self._values['recent_channel_%s' %channel]['m1']
        if (m2==[]):
            m2 = self._values['recent_channel_%s' %channel]['m2']
        if (clock==[]):
            clock = self._values['recent_channel_%s' %channel]['clock']

        if not ( (len(w) == self._numpoints) and (len(m1) == self._numpoints) and (len(m2) == self._numpoints)):
            logging.error(__name__ + ' : one (or more) lengths of waveforms do not match with numpoints')

        self.send_waveform(w,m1,m2,filename,clock)
        self.do_set_filename(filename, channel)

    def set_all_channels_on(self):
        for i in range(1, 3):
            self.set_status('on',i)
    
        

    def send_sequence(self,wfs,rep,wait,goto,logic_jump,filename):
        '''
        Sends a sequence file (for the moment only for ch1)
        Inputs (mandatory):
           wfs:  list of filenames
        Output:
            None
        '''
        logging.debug(__name__ + ' : Sending sequence %s to instrument' % filename)
        N = str(len(rep))
        try:
            wfs.remove(N*[None])
        except ValueError:
            pass
        s1 = 'MMEM:DATA "%s",' % filename

        if len(shape(wfs)) ==1:
            s3 = 'MAGIC 3001\n'
            s5 = ''
            for k in range(len(rep)):
                s5 = s5+ '"%s",%s,%s,%s,%s\n'%(wfs[k],rep[k],wait[k],goto[k],logic_jump[k])

        else:
            s3 = 'MAGIC 3002\n'
            s5 = ''
            for k in range(len(rep)):
                s5 = s5+ '"%s","%s",%s,%s,%s,%s\n'%(wfs[0][k],wfs[1][k],rep[k],wait[k],goto[k],logic_jump[k])

        s4 = 'LINES %s\n'%N
        lenlen=str(len(str(len(s5) + len(s4) + len(s3))))
        s2 = '#' + lenlen + str(len(s5) + len(s4) + len(s3))


        mes = s1 + s2 + s3 + s4 + s5
        self.write(mes)

    def send_sequence2(self,wfs1,wfs2,rep,wait,goto,logic_jump,filename):
        '''
        Sends a sequence file
        Inputs (mandatory):
            wfs1:  list of filenames for ch1 (all must end with .pat)
            wfs2: list of filenames for ch2 (all must end with .pat)
            rep: list
            wait: list
            goto: list
            logic_jump: list
            filename: name of output file (must end with .seq)
        Output:
            None
        '''
        logging.debug(__name__ + ' : Sending sequence %s to instrument' % filename)


        N = str(len(rep))
        s1 = 'MMEM:DATA "%s",' % filename
        s3 = 'MAGIC 3002\n'
        s4 = 'LINES %s\n'%N
        s5 = ''


        for k in range(len(rep)):
            s5 = s5+ '"%s","%s",%s,%s,%s,%s\n'%(wfs1[k],wfs2[k],rep[k],wait[k],goto[k],logic_jump[k])

        lenlen=str(len(str(len(s5) + len(s4) + len(s3))))
        s2 = '#' + lenlen + str(len(s5) + len(s4) + len(s3))


        mes = s1 + s2 + s3 + s4 + s5
        self.write(mes)

   

    def load_and_set_sequence(self,wfs,rep,wait,goto,logic_jump,filename):
        '''
        Loads and sets the awg sequecne
        '''
        self.send_sequence(wfs,rep,wait,goto,logic_jump,filename)
        self.set_sequence(filename)

    def do_get_AWG_model(self):
        return 'AWG520'