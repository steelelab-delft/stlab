# This module implements the basic class for pulses as well as some very
# generic pulse types.
#
# author: Wolfgang Pfaff
# Modified by: Sarwan Peiter

import numpy as np
from copy import deepcopy


def cp(pulse, *arg, **kw):
    """
    create a copy of the pulse, configure it by given arguments (using the
        call method of the pulse class), and return the copy
    """
    pulse_copy = deepcopy(pulse)

    return pulse_copy(*arg, **kw)



def apply_modulation(I_env, Q_env, tvals, mod_frequency,
                     phase=0, phi_skew=0, alpha=1):
    '''
    Applies single sideband modulation, requires timevals to make sure the
    phases are correct.
    Input args:
        I_env (array)
        Q_env (array)
        tvals (array):              in seconds
        mod_frequency(float):       in Hz
        phase (float):              in degree
        phi_skew (float):           in degree
        alpha (float):              ratio
    returns:
        [I_mod, Q_mod] = M*mod*[I_env, Q_env]
    Signal = predistortion * modulation * envelope
    See Leo's notes on mixer predistortion in the docs for details
    [I_mod] = [1        tan(phi-skew)] [cos(wt+phi)   sin(wt+phi)] [I_env]
    [Q_mod]   [0  sec(phi-skew)/alpha] [-sin(wt+phi)  cos(wt+phi)] [Q_env]
    The predistortion * modulation matrix is implemented in a single step
    using the following matrix
    M*mod = [cos(x)-tan(phi-skew)sin(x)      sin(x)+tan(phi-skew)cos(x) ]
            [-sin(x)sec(phi-skew)/alpha  cos(x)sec(phi-skew)/alpha]
    '''

    tan_phi_skew = np.tan(2 * np.pi * phi_skew / 360)
    sec_phi_alpha = 1 / (np.cos(2 * np.pi * phi_skew / 360) * alpha)

    I_mod = (I_env * (np.cos(2 * np.pi * (mod_frequency * tvals +
                                          phase / 360)) - tan_phi_skew *
                      np.sin(2 * np.pi * (mod_frequency * tvals +
                                          phase / 360))) +
             Q_env * (np.sin(2 * np.pi * (mod_frequency * tvals +
                                          phase / 360)) + tan_phi_skew *
                      np.cos(2 * np.pi * (mod_frequency * tvals + phase / 360))))

    Q_mod = (-1 * I_env * sec_phi_alpha * np.sin(2 * np.pi * (mod_frequency *
                                                              tvals + phase / 360.)) +
             + Q_env * sec_phi_alpha * np.cos(2 * np.pi * (
                 mod_frequency * tvals + phase / 360.)))
    return [I_mod, Q_mod]

class Pulse:
    """
    A generic pulse. The idea is that a certain implementation of a pulse
    is able to return a 'waveform', which we define as an array of time values
    and an array of amplitude values for each channel of the pulse.
    There are three stages of configuring a pulse:
    1) Implementation of the specific class
    2) when adding to a sequence element (when __call__ is implemented
       in that way)
    3) when the sequence element object calls wf() (this 'finalizes' the
       numerical values).
    A pulse does not yet know about any discretization using a clock.
    This is all done in the sequence element.
    See the examples for more information.
    """


    def __init__(self, name):
        self.length = None
        self.name = name
        self.channels = []
        self.start_offset = 0
        # the time within (or outside) the pulse that is the 'logical' start
        # of the pulse (for referencing)
        self.stop_offset = 0
        # the time within (or outside) the pulse that is the 'logical' stop
        # of the pulse (for referencing)

        self._t0 = None
        self._clock = None

    def __call__(self):
        return self

    def get_wfs(self, tvals):
        """
        The time values in tvals can always be given as one array of time
        values, or as a separate array for each channel of the pulse.
        """
        wfs = {}
        for c in self.channels:
            if type(tvals) == dict:
                wfs[c] = self.chan_wf(c, tvals[c])
            else:
                if hasattr(self, 'chan_wf'):
                    wfs[c] = self.chan_wf(c, tvals)
                elif hasattr(self, 'wf'):
                    wfs = self.wf(tvals)
                else:
                    raise Exception('Could not find a waveform-generator function!')

        return wfs

    def t0(self):
        """
        returns start time of the pulse. This is typically
        set by the sequence element at the time the pulse is added to the
        element.
        """
        return self._t0

    def effective_start(self):
        return self._t0 + self.start_offset

    def end(self):
        """
        returns the end time of the pulse.
        """
        return self._t0 + self.length

    def effective_stop(self):
        return self.end() - self.stop_offset

    def effective_length(self):
        return self.length - self.start_offset - self.stop_offset


# Some simple pulse definitions.
class SquarePulse(Pulse):

    def __init__(self, channel=None, channels=None, name='square pulse', **kw):
        Pulse.__init__(self, name)
        if channel is None and channels is None:
            raise ValueError('Must specify either channel or channels')
        elif channels is None:
            self.channel = channel  # this is just for convenience, internally
            # this is the part the sequencer element wants to communicate with
            self.channels.append(channel)
        else:
            self.channels = channels
        self.amplitude = kw.pop('amplitude', 0)
        self.length = kw.pop('length', 0)

    def __call__(self, **kw):
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length)
        self.channel = kw.pop('channel', self.channel)
        self.channels = kw.pop('channels', self.channels)
        self.channels.append(self.channel)
        return self

    def chan_wf(self, chan, tvals):
        return np.ones(len(tvals)) * self.amplitude


class CosPulse(Pulse):

    def __init__(self, channel, name='cos pulse', **kw):
        Pulse.__init__(self, name)

        self.channel = channel  # this is just for convenience, internally
        self.channels.append(channel)
        # this is the part the sequencer element wants to communicate with
        self.frequency = kw.pop('frequency', 1e6)
        self.amplitude = kw.pop('amplitude', 0.)
        self.length = kw.pop('length', 0.)
        self.phase = kw.pop('phase', 0.)

    def __call__(self, **kw):
        self.frequency = kw.pop('frequency', self.frequency)
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length)
        self.phase = kw.pop('phase', self.phase)
        channel = kw.pop('channel', None)
        if channel is not None:
            self.channel = channel
            self.channels = [self.channel]
        self.channels = kw.pop('channels', self.channels)

        return self

    def chan_wf(self, chan, tvals):
        return self.amplitude * np.cos(2 * np.pi *
                                       (self.frequency * tvals +
                                        self.phase / 360.))


class LinearPulse(Pulse):

    def __init__(self, channel=None, channels=None, name='linear pulse', **kw):
        """ Pulse that performs linear interpolation between two setpoints """
        Pulse.__init__(self, name)
        if channel is None and channels is None:
            raise ValueError('Must specify either channel or channels')
        elif channels is None:
            self.channel = channel  # this is just for convenience, internally
            # this is the part the sequencer element wants to communicate with
            self.channels.append(channel)
        else:
            self.channels = channels

        self.start_value = kw.pop('start_value', 0)
        self.end_value = kw.pop('end_value', 0)
        self.length = kw.pop('length', 0)

    def __call__(self, **kw):
        self.start_value = kw.pop('start_value', self.start_value)
        self.end_value = kw.pop('end_value', self.end_value)
        self.length = kw.pop('length', self.length)
        channel = kw.pop('channel', None)
        if channel is not None:
            self.channel = channel
            self.channels = [self.channel]
        self.channels = kw.pop('channels', self.channels)
        return self

    def chan_wf(self, chan, tvals):
        return np.linspace(self.start_value, self.end_value, len(tvals))



class clock_train(Pulse):

    def __init__(self, channel, name='clock train', **kw):
        Pulse.__init__(self, name)
        self.channel = channel
        self.channels.append(channel)

        self.amplitude = kw.pop('amplitude', 0.1)
        self.cycles = kw.pop('cycles', 100)
        self.nr_up_points = kw.pop('nr_up_points', 2)
        self.nr_down_points = kw.pop('nr_down_points', 2)
        self.length = self.cycles * (self.nr_up_points + self.nr_down_points) * 1e-9

    def __call__(self, **kw):
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.cycles = kw.pop('cycles', self.cycles)
        self.nr_up_points = kw.pop('nr_up_points', self.nr_up_points)
        self.nr_down_points = kw.pop('nr_down_points', self.nr_down_points)
        self.length = self.cycles * (self.nr_up_points + self.nr_down_points) * 1e-9

        if channel is not None:
            self.channel = channel
            self.channels = [self.channel]
        self.channels = kw.pop('channels', self.channels)

        return self

    def chan_wf(self, chan, tvals):
        unit_cell = []
        for i in np.arange(self.nr_up_points):
            unit_cell.append(self.amplitude)
        for i in np.arange(self.nr_down_points):
            unit_cell.append(0)
        wf = unit_cell * self.cycles

        return wf


class marker_train(Pulse):

    def __init__(self, channel, name='marker train', **kw):
        Pulse.__init__(self, name)
        self.channel = channel
        self.channels.append(channel)

        self.amplitude = kw.pop('amplitude', 1)
        self.nr_markers = kw.pop('nr_markers', 100)
        self.marker_length = kw.pop('marker_length', 15e-9)
        self.marker_separation = kw.pop('marker_separation', 100e-9)

    def __call__(self, **kw):
        self.channel = kw.pop('channel', self.channel)
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.nr_markers = kw.pop('nr_markers', self.nr_markers)
        self.marker_length = kw.pop('marker_length', self.marker_length)
        self.marker_separation = kw.pop('marker_separation',
                                        self.marker_separation)

        self.channels = []
        self.channels.append(self.channel)
        self.length = self.nr_markers * self.marker_separation
        return self

    def chan_wf(self, chan, tvals):
        # Using lists because that is default, I expect arrays also work
        # but have not tested that. MAR 15-2-2016
        unit_cell = list(np.ones(round(self.marker_length * 1e9)))
        unit_cell.extend(list(np.zeros(
            round((self.marker_separation - self.marker_length) * 1e9))))
        wf = unit_cell * self.nr_markers
        # Added this check because I had issues with this before it can occur
        # when e.g. giving separations that are not in sub ns resolution
        if(len(wf) != round(self.length * 1e9)):
            raise ValueError('Waveform length is not equal to expected length')

        return wf



class MW_IQmod_pulse(Pulse):

    '''
    Block pulse on the I channel modulated with IQ modulation.
    kwargs:
        amplitude (V)
        length (s)
        mod_frequency (Hz)
        phase (deg)
        phaselock (bool)
    I_env is a block pulse
    transformation:
    [I_mod] = [cos(wt+phi)   0] [I_env]
    [Q_mod]   [-sin(wt+phi)  0] [0]
    '''

    def __init__(self, name, I_channel, Q_channel, **kw):
        super().__init__(name)
        self.I_channel = I_channel
        self.Q_channel = Q_channel
        self.channels = [I_channel, Q_channel]

        self.mod_frequency = kw.pop('mod_frequency', 1e6)
        self.amplitude = kw.pop('amplitude', 0.1)
        self.length = kw.pop('length', 1e-6)
        self.phase = kw.pop('phase', 0.)
        self.phaselock = kw.pop('phaselock', True)
        self.alpha = kw.pop('alpha', 1)
        self.phi_skew = kw.pop('phi_skew', 0)

    def __call__(self, **kw):
        self.mod_frequency = kw.pop('mod_frequency', self.mod_frequency)
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length)
        self.phase = kw.pop('phase', self.phase)
        self.phaselock = kw.pop('phaselock', self.phaselock)
        self.alpha = kw.pop('alpha', self.alpha)
        self.phi_skew = kw.pop('phi_skew', self.phi_skew)
        return self

    def chan_wf(self, chan, tvals):
        idx0 = np.where(tvals >= tvals[0])[0][0]
        idx1 = np.where(tvals <= tvals[0] + self.length)[0][-1] + 1
        wf = np.zeros(len(tvals))
        if not self.phaselock:
            tvals = tvals.copy() - tvals[idx0]
        I_mod, Q_mod = apply_modulation(
            self.amplitude*np.ones(len(tvals)),
            np.zeros(len(tvals)), tvals[idx0:idx1],
            mod_frequency=self.mod_frequency, phase=self.phase,
            phi_skew=self.phi_skew, alpha=self.alpha)
        if chan == self.I_channel:
            wf[idx0:idx1] += I_mod
        elif chan == self.Q_channel:
            wf[idx0:idx1] += Q_mod
        return wf

class SSB_DRAG_pulse(Pulse):

    '''
    Gauss pulse on the I channel, derivative of Gauss on the Q channel.
    modulated with Single Sideband (SSB)  modulation.
    Required arguments:
        name (str) : base name of the pulse
        I_channel (str) : name of the channel on which to act (as defined in pular)
        Q_channel (str) : " "
    kwargs:
        amplitude (V)
        sigma (s)
        nr_sigma (int) (default=4)
        motzoi ( ) (default=0)
        mod_frequency (Hz)
        phase (deg)
        phaselock (bool)
        alpha (arb. units): QI amplitude
        phi_skew (deg) :    phase skewness
    I_env is a gaussian
    Q_env is the derivative of a gaussian
    The envelope is transformation:
    Signal = predistortion * modulation * envelope
    See Leo's notes on mixer predistortion in the docs for details
    [I_mod] = [1        tan(phi-skew)] [cos(wt+phi)   sin(wt+phi)] [I_env]
    [Q_mod]   [0  sec(phi-skew)/alpha] [-sin(wt+phi)  cos(wt+phi)] [Q_env]
    The predistortion * modulation matrix is implemented in a single step using
    the following matrix
    M*mod = [cos(x)-tan(phi-skew)sin(x)      sin(x)+tan(phi-skew)cos(x) ]
            [-sin(x)sec(phi-skew)/alpha  cos(x)sec(phi-skew)/alpha]
    where: x = wt+phi
    Reduces to a Gaussian pulse if motzoi == 0
    Reduces to an unmodulated pulse if mod_frequency == 0
    '''

    def __init__(self, name, I_channel, Q_channel, **kw):
        super().__init__(name)
        self.I_channel = I_channel
        self.Q_channel = Q_channel
        self.channels = [I_channel, Q_channel]

        self.amplitude = kw.pop('amplitude', 0.1)
        self.sigma = kw.pop('sigma', 0.25e-6)
        self.nr_sigma = kw.pop('nr_sigma', 4)
        self.motzoi = kw.pop('motzoi', 0)

        self.mod_frequency = kw.pop('mod_frequency', 1e6)
        self.phase = kw.pop('phase', 0.)
        self.phaselock = kw.pop('phaselock', True)

        self.alpha = kw.pop('alpha', 1)        # QI amp ratio
        self.phi_skew = kw.pop('phi_skew', 0)  # IQ phase skewness

        self.length = self.sigma * self.nr_sigma

    def __call__(self, **kw):
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.sigma = kw.pop('sigma', self.sigma)
        self.nr_sigma = kw.pop('nr_sigma', self.nr_sigma)
        self.motzoi = kw.pop('motzoi', self.motzoi)
        self.mod_frequency = kw.pop('mod_frequency', self.mod_frequency)
        self.phase = kw.pop('phase', self.phase)
        self.phaselock = kw.pop('phaselock', self.phaselock)

        self.length = self.sigma * self.nr_sigma
        return self

    def chan_wf(self, chan, tvals):
        idx0 = np.where(tvals >= tvals[0])[0][0]
        idx1 = np.where(tvals <= tvals[0] + self.length)[0][-1] + 1
        wf = np.zeros(len(tvals))
        t = tvals - tvals[0]  # Gauss envelope should not be displaced
        mu = self.length/2.0
        if not self.phaselock:
            tvals = tvals.copy() - tvals[idx0]

        gauss_env = self.amplitude*np.exp(-(0.5 * ((t-mu)**2) / self.sigma**2))
        deriv_gauss_env = self.motzoi * -1 * (t-mu)/(self.sigma**1) * gauss_env
        # substract offsets
        gauss_env -= (gauss_env[0]+gauss_env[-1])/2.
        deriv_gauss_env -= (deriv_gauss_env[0]+deriv_gauss_env[-1])/2.

        # Note prefactor is multiplied by self.sigma to normalize
        if chan == self.I_channel:
            I_mod, Q_mod = apply_modulation(gauss_env, deriv_gauss_env,
                                            tvals[idx0:idx1],
                                            mod_frequency=self.mod_frequency,
                                            phase=self.phase,
                                            phi_skew=self.phi_skew,
                                            alpha=self.alpha)
            wf[idx0:idx1] += I_mod

        if chan == self.Q_channel:
            I_mod, Q_mod = apply_modulation(gauss_env, deriv_gauss_env,
                                            tvals[idx0:idx1],
                                            mod_frequency=self.mod_frequency,
                                            phase=self.phase,
                                            phi_skew=self.phi_skew,
                                            alpha=self.alpha)
            wf[idx0:idx1] += Q_mod

        return wf

