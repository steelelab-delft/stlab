"""Module for the calculation of transmission line impedances

Most functions require a dictionary with specific elements regarding circuit parameters in it.::

    params = {
        'Z0': 64.611, # characteristic impedance of TL resonator (e.g. geometric and kinetic), in Ohm
        'Cj': 1.77e-15, # Capacitance of the junction (RCSJ model) loading the TL resonator, in F
        'Z0p': 50, # reference impedance of the input line, in Ohm
        'Lg': 1.0432952403781536e-10, # geometric inductance of the junction leads loading the TL resonator, in H
        'Rj': 1027.6618763504205, # Resistance of the junction (RCSJ model) loading the TL resonator, in Ohm
        'n': 2.876042565429968, # refraction index for the TL resonator (v_ph = c / n)
        'type': 'lambda/2', # expected type of TL resonator. Only used in Zincircuit_approx. Can be 'lambda/2', 'lambda/4'
        'alpha': 0.0060728306929787035,  # attenuation constant for the TL resonator. This mainly sets the internal losses, in 1/m
        'Lj': 2.0916766016363636e-10, # Josephson inductance of the junction (RCSJ model) loading the TL resonator, in H
        'Pin': -122, # input power at the coupler of the TL resonator, in dBm
        'Cs': 2.657e-11, # shunt capacitance of the coupler, in F
        'l': 0.006119 # length of the TL resonator, in m
        }

The model calculated here is valid for a transmission line resonator coupled to the input line via a shunt capacitance Cs.
At the far end, the TL resonator can be loaded by a RCSJ-type junction with an extra series inductor Lg and parallel capacitance Cg.

.. figure::  ../images/TLmodel.jpg
   :align:   center

   Circuit model used for :code:`TLmodel.py`.

For more details see `A ballistic graphene superconducting microwave circuit <https://www.nature.com/articles/s41467-018-06595-2/>`_

Functions
=========

"""
import numpy as np
import scipy.constants as const
from scipy.optimize import minimize
from scipy.optimize import brentq
import copy


def S11theo(f, f0, kint, kext):
    """Lorentzian absortion function

    Approximate formula for a Series RLC circuit capacitively
    coupled on one side to a transmission line. The frequencies can
    be either angular or 'real' ones, as long as all of them have the 
    same type.

    Parameters
    ----------
    f : float or array of float
        Frequency parameter
    f0 : float
        Resonance frequency
    kint : float
        Internal linewidth or loss rate
    kext : float
        External linewidth or loss rate

    Returns
    -------
    float or array of float
        Values of S11 for the given input parameters

    """
    df = f - f0
    return -1. + (2. * kext) / (kext + kint + 2j * df)


def S11(Zin, params):
    """Exact expression of S11 for a given input impedance and parameters

    Parameters
    ----------
    Zin : complex or array of complex
        Load impedance
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    result : complex or array of complex
        Values of S11 for the given input parameters

    """
    Z0p = params['Z0p']
    result = (Zin - Z0p) / (Zin + Z0p)
    return result


def Zincircuit(omega, params):
    """Analytical dalculation of input impedance of a TL resonator with a shunt capacitor

    Is only valid for a shunt coupler and depends on the definition of :func:`Zload`.
    :func:`Zload` is the impedance of the load on the far end of the TL resonator (opposite the coupler).
    Examples can be an open/short/junction end of the transmission line resonator.
    This is an analytical calculation using transmission line formulas (from Pozar).
    There are no lumped element approximations or equivalents involved.

    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    Zin : complex or array of complex
        Impedance seen at the resonator input

    """
    l = params['l']
    Z0 = params['Z0']
    vph = const.c / params['n']
    beta = omega / vph
    al = alpha(omega, params)
    gamma = al + 1j * beta
    Zin = Zload(omega, params)
    Zin = ZTL(Z0, Zin, gamma * l)
    Zc = Zcoup(omega, params)
    Zin = Zparallel(Zin, Zc)
    return Zin


def Zincircuit_approx(omega, params):
    """Lumped equivalent calculation of input impedance of a TL resonator with a shunt capacitor

    Is only valid for a shunt coupler and assumes the load impedance is :code:`params['Lg']`.
    This is a lumped equivalent calculation of the TL resonator with either an open or a short end.


    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    Zin : complex or array of complex
        Impedance seen at the resonator input

    """
    l = params['l']
    Z0 = params['Z0']
    al = alpha(omega, params)
    Zc = Zcoup(omega, params)
    vph = const.c / params['n']
    if params['type'] == 'lambda/2':
        lj = params['Lg'] / (Z0 / vph)
        w0u = np.pi * vph / (l + lj)
        Ll = Z0 * np.pi / 2 / w0u
        Cl = 2 / np.pi / Z0 / w0u
    elif params['type'] == 'lambda/4':
        lj = 0
        w0u = np.pi * vph / 2 / (l + lj)
        Ll = Z0 * np.pi / 4 / w0u
        Cl = 4 / np.pi / Z0 / w0u
    else:
        raise ValueError(
            'Invalid boundary condition. Must be lambda/2 or lambda/4.')
    Rl = Z0 * al * l
    Zin = Rl + 1j * omega * Ll + 1 / (1j * omega * Cl)
    Zc = Zcoup(omega, params)
    Zin = Zparallel(Zin, Zc)
    return Zin


def ZTL(Z0, Zl, gammal):
    """Impedance of a general terminated transmission line

    Calculates the input impedance of a termniated transmission line with a given load impedance

        
    .. math:: \\gamma_l = \\alpha + i\\beta = \\alpha+i\\frac{\\omega}{v_{\\rm ph}}

    Parameters
    ----------
    Z0 : complex
        line impedance
    Zl : complex
        load impedance
    gammal : complex
        propagation constant including losses

    Returns
    -------
    result : complex
        Impedance of the terminated TL

    """
    result = Z0 * (Zl + Z0 * np.tanh(gammal)) / (Z0 + Zl * np.tanh(gammal))
    return result


def Zcoup(omega, params):
    """Impedance of a general capacitor

    Here used for the shunt capacitor (coupler) at the start of the TL

    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    complex
        shunt capacitor impedance

    """
    C = params['Cs']
    return 1 / (1j * omega * C)


def Zload(omega, params):
    """Impedance of a load at the far end of the TL resonator

    Currently includes the possiblitity for an RCSJ and a capacitor as load

    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    Z : complex
        load impedance

    """
    L = params['Lg']
    Z = 1j * omega * L
    if 'Lj' in params:
        Lj = params['Lj']
        Cj = params['Cj']
        Rj = params['Rj']
        Zj = (1j * Lj * Rj * omega) / (
            Rj + 1j * Lj * omega - Cj * Lj * Rj * omega**2.)
        Z += Zj
    if 'Cg' in params:
        Cg = params['Cg']
        if Cg is not 0:
            Z = Zparallel(Z, 1 / (1j * omega * Cg))
    return Z


def Zparallel(*args):
    """Parallel impedance of a collection of impedances

    Parameters
    ----------
    *args : complex
        Values of impedances to be put in parallel

    Returns
    -------
    result : complex
        parallel impedance

    """
    result = 0
    for z in args:
        result += 1 / z
    result = 1 / result
    return result


def Vin(omega, params):
    """Voltage phasor at the input

    If Pin is in params, it is used to calculate the actual amplitudes.
    If not, we assume an amplitude of 1V for the incoming wave.

    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    result : complex
        Voltage phasor at the input

    """
    if 'Pin' in params:
        V0 = PintoV0(params)  #V0 is the incoming wave amplitude
    else:
        V0 = 1
    result = V0 * (1 + S11(Zincircuit(omega, params), params))
    return result


def Vx(x, omega, params):
    """Voltage phasor at a given distance along the TL

    Distance x counts from the load (at 0) to l (at input)

    Parameters
    ----------
    x : float
        Position along the TL to calculate the voltage at, counting from the load (at 0) to l (at input)
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    result : complex
        Voltage phasor at a given distance along the TL

    """
    l = params['l']
    Z0 = params['Z0']
    vph = const.c / params['n']
    beta = omega / vph
    al = alpha(omega, params)
    gamma = al + 1j * beta
    GammaL = (Zload(omega, params) - Z0) / (Zload(omega, params) + Z0)
    result = Vin(
        omega, params) / (np.exp(gamma * l) + GammaL * np.exp(-gamma * l)) * (
            np.exp(gamma * x) + GammaL * np.exp(-gamma * x))
    return result


def omega0(params, wws=None):  #Range wws in rad/sec
    """Finds the approximate angular resonance frequency from a generic circuit impedance

    This is an approximation which can then be used to a fitting function as starting value

    Parameters
    ----------
    params : dict
        Dictionary containing model parameters
    wws : None or array, optional
        Angular frequency range to evaluate the circuit impedance at. By default 2-10 GHz * 2pi

    Returns
    -------
    wres : float
        Approximate angular resonance frequency

    """
    if wws is None:  #Default to 2Ghz to 10Ghz search range
        ffs = np.linspace(2, 10, 5001) * 1e9
        wws = 2. * np.pi * ffs
    else:
        ffs = wws / 2 / np.pi

    i0 = np.argmax(np.power(np.diff(np.imag(Zincircuit(wws, params))),
                            2.))  #find derivative maximum
    # fres = ffs[i0]
    wres = wws[i0]
    return wres
    '''
#    print('{:e}'.format(fres))
    a = wws[i0-2] #start of bracketing interval
    b = wws[i0+2] #end of bracketin interval
    myfunc = lambda x: np.imag(Zincircuit(x,params)) #Function for root


    try:    
        wres = brentq(myfunc,a,b,xtol = 1) #Find root
    except ValueError:
        print('omega0: Warning, bad bracketing\n')

    fres = wres/2/np.pi
    return wres
    '''


def f0(params, ffs=None):  #Range ffs in Hz
    """Finds the approximate resonance frequency in Hz from a generic circuit impedance

    This is an approximation which can then be used to a fitting function as starting value

    Parameters
    ----------
    params : dict
        Dictionary containing model parameters
    ffs : None or array, optional
        Frequency range in Hz to evaluate the circuit impedance at. By default 2-10 GHz

    Returns
    -------
    wres : float
        Approximate resonance frequency in Hz

    """
    if ffs is None:  #Default to 2Ghz to 10Ghz search range
        ffs = np.linspace(2, 10, 5001) * 1e9
        wws = 2. * np.pi * ffs
    else:
        wws = ffs * 2 * np.pi
    return omega0(params, wws) / 2 / np.pi


def Zx(x, omega, params):
    """Impedance at a given distance along the TL

    Distance x counts from the load (at 0) to l (at input)

    Parameters
    ----------
    x : float
        Position along the TL to calculate the impedance at, counting from the load (at 0) to l (at input)
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    result : complex
        Impedance at a given distance along the TL

    """
    # l = params['l']
    Z0 = params['Z0']
    vph = const.c / params['n']
    beta = omega / vph
    al = alpha(omega, params)
    gamma = al + 1j * beta
    Zl = Zload(omega, params)
    result = Z0 * (Zl + 1j * Z0 * np.tan(-1j * gamma * x)) / (
        Z0 + 1j * Zl * np.tan(-1j * gamma * x))
    return result


def PintoV0(params):
    """Conversion from power to voltage

    Parameters
    ----------
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    float
        Incoming voltage amplitude for a given power

    """
    Plin = np.power(10, params['Pin'] / 10) * 1e-3
    return np.sqrt(2. * params['Z0p'] * Plin)


def Ix(x, omega, params):
    """Current phasor at a given distance along the TL

    Distance x counts from the load (at 0) to l (at input)

    Parameters
    ----------
    x : float
        Position along the TL to calculate the current at, counting from the load (at 0) to l (at input)
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    complex
        Current phasor at a given distance along the TL

    """
    return Vx(x, omega, params) / Zx(x, omega, params)


def Vj(omega, params):
    """Voltage at the far end of the TL across a Josephson junction (RCSJ)
    
    If there is a Lj and Cg in params, returns the voltage accross the junction (complex).  Else, just the load voltage

    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    Vl : complex
        Voltage phasor at the far end of the TL

    """
    Vl = Vx(0, omega, params)
    if 'Lj' in params:
        Zl = Zload(omega, params)
        if 'Cg' in params:
            Zl0 = 1 / (1j * omega * params['Cg']) * Zl / (
                1 / (1j * omega * params['Cg']) - Zl)
            Ij = Vl / Zl0
        else:
            Ij = Vl / Zl
        result = Vl - Ij * 1j * omega * params['Lg']
        return result
    else:
        return Vl


def Ij(omega, params):
    """Total current going out the far end of the TL

    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    Vl : complex
        Current phasor through the load

    """
    Vl = Vx(0, omega, params)
    Zl = Zload(omega, params)
    Il = Vl / Zl
    return Il


def alpha(omega, params):
    """Attenuation constant of a TL

    Parameters
    ----------
    omega : float or array of float
        Angular frequency
    params : dict
        Dictionary containing model parameters

    Returns
    -------
    float
        Attenuation constant given in the parameters

    """
    return params['alpha']


def FindParFromRes(params, w0, a, b, par='Lj', wws=None):
    """Function to find value of a parameter to match a given resonance frequency

    Finds approximate value of par to have an angular resonance frequency of w0.
    a,b is the bracketing interval.
    In our processing, the objective is to extract the load parameters from given 
    resonance features, like the resonance frequency.
    Given w0, this function provides an initial estimate of these parameters to then perform 
    the final fit such that the resonance frequency will start close to this value
    (for fit convergence).
    
    Parameters
    ----------
    params : dict
        Dictionary containing model parameters
    w0 : float
        Desired angular resonance frequency
    a : float
        Bottom of bracketing interval for the parameter
    b : float
        Top of bracketing interval for the parameter
    par : str, optional
        Key of the parameter in :code:`params` to be swept
    wws : None or array, optional
        Angular frequency range to evaluate the circuit impedance at.

    Returns
    -------
    par0 : float
        Parameter value that satisfies desired resonance frequency for the given parameters

    """

    newparams = copy.deepcopy(params)

    def myfunc(x, w0, par, params, wws=None):
        newparams[par] = x
        result = omega0(params, wws)
        return result - w0


#    from matplotlib import pyplot as plt
#    wws = np.linspace(2.,10.,5001)*1e9*2*np.pi
#    newparams[par] = a
#    plt.plot(wws/2/np.pi,np.imag(Zincircuit(wws,newparams)))
#    newparams[par] = b
#    plt.plot(wws/2/np.pi,np.imag(Zincircuit(wws,newparams)))
#    plt.show()
#    print(myfunc(a,w0,par,newparams,wws))
#    print(myfunc(b,w0,par,newparams,wws))

    par0 = brentq(myfunc, a, b, args=(w0, par, newparams, wws))  #Find root
    return par0

if __name__ == "__main__":

    #Readjusted values
    params = {
        'Z0': 64.611,
        'Cj': 1.77e-15,
        'Z0p': 79.400384766937506,
        'Lg': 1.0432952403781536e-10,
        'Rj': 1027.6618763504205,
        'n': 2.876042565429968,
        'type': 'lambda/2',
        'alpha': 0.0060728306929787035,
        'Lj': 2.0916766016363636e-10,
        'Pin': -122,
        'Cs': 2.657e-11,
        'l': 0.006119
    }
    wres = 49685604684.2

    a = 0
    b = 1e-9

    result = FindParFromRes(params, wres, a, b, par='Lj', wws=None)
    print(result)
