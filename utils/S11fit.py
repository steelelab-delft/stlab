"""Module for fitting resonance line shapes to different circuit models

This module contains the functions necessary to fit some general lorentizian to
simulations or measurements.  The main function is "fit" and is imported with
stlab as "stlab.S11fit".  All other functions in this module are there to
supplement this fitting function or are not generally used.

"""
import numpy as np
from scipy.signal import savgol_filter as smooth
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters, Parameter, report_fit

pi = np.pi

def newparams(f0=1,Qint=100,Qext=200,theta=0,a=1,b=0,c=0,ap=0,bp=0):
    """Makes new Parameters object compatible with fitting routine

    A new lmfit.Parameters object is created using the given values.  Default
    values are filled in for ommited parameters.  The fit model is:

    .. math:: \Gamma'(\omega)=(a+b\omega+c\omega^2)\exp(j(a'+b'\omega))\cdot
        \Gamma(\omega,Q_\\textrm{int},Q_\\textrm{ext},\\theta),

    Parameters
    ----------
    f0 : float, optional
        Resonance frequency
    Qint : float, optional
        Internal quality factor
    Qext : float, optional
        External quality factor
    theta : float, optional
        Rotation angle to compensate additive background effects.  Should be
        close to 0 for good fits.
    a : float, optional
        Background magnitude offset
    b : float, optional
        Background magnitude linear slope
    c : float, optional
        Background magnitude quadratic term
    ap : float, optional
        Background phase offset
    bp : float, optional
        Background phase slope

    Returns
    -------
    params : lmfit.Parameters
        lmfit fit object containing the provided parameters

    """

    params = lmfit.Parameters()

    params.add('a', value= a, vary=True)
    params.add('b', value= b, vary=True)
    params.add('c', value= c, vary=True)
    params.add('ap', value= ap, vary=True)
    params.add('bp', value= bp, vary=True)
    params.add('cp', value= 0, vary=False)

    params.add('Qint', value=Qint,vary=True,min = 0)
    params.add('Qext', value=Qext,vary=True,min = 0)
    params.add('f0', value=f0,vary=True)
    params.add('theta', value=theta,vary=True)

    return params



def realimag(array):
    """Makes alternating real and imaginary part array from complex array

    Takes an array-like object of complex number elements and generates a
    1-D array aleternating the real and imaginary part of each element of the
    original array.  If array = (z1,z2,...,zn), then this function returns
    (x1,y1,x2,y2,...,xn,yn) where xi = np.real(zi) and yi=np.imag(zi).

    Parameters
    ----------
    array : array_like of complex
        1-D array of complex numbers

    Returns
    -------
    numpy.ndarray
        New array of alternating real and imag parts of each element of
        original array

    """
    return np.array([(x.real, x.imag) for x in array]).flatten()

def un_realimag(array):
    """Makes complex array from alternating real and imaginary part array

    Performs the reverse operation to realimag

    Parameters
    ----------
    array : array_like of float
        1-D array of real numbers.  Should have an even number of elements.

    Returns
    -------
    numpy.ndarray of numpy.complex128
        1-D array of complex numbers built by taking every two elements of
        original array as the real and imaginary parts

    """
    z = []
    for x,y in zip(array[::2],array[1::2]):
        z.append(x+1j*y)
    return np.array(z)

def phaseunwrap(array):
    """Removes a global phase slope from a complex array

    Unwraps the phase of a sequence of complex numbers and subtracts the average
    slope of the phase (desloped phase).

    Parameters
    ----------
    array : array_like of complex
        1-D array of complex numbers

    Returns
    -------
    numpy.ndarray of numpy.complex128
        Same array as original but with phase slope removed (0 average phase
        slope)

    """
    data = np.asarray(array)
    phase = np.unwrap(np.angle(data))
    avg = np.average(np.diff(phase))
    data = [x*np.exp(-1j*avg*i) for i,x in enumerate(data)]
#    print(np.average(np.diff(np.angle(data))))
    return np.asarray(data)

def getwidth_phase(i0,vec,margin):
    """Finds indices for peak width around given maximum position

    Auxiliary function for fit.  Given the complex array "vec" assuming "i0"
    is the resonance index, this function finds resonance peak width from the
    phase derivative of the signal.

    Parameters
    ----------
    i0 : int
        Array index of resonance
    vec : array_like of complex
        Complex array with resonance data
    margin : int
        Smoothing margin used on data.  Needed to remove spureous increases in
        the phase array that occur at the head and tail of vec after smoothing.
        Should be an odd number

    Returns
    -------
    (int, int)
        Indices of the lower and upper estimated edges of the resonance peak

    """
    maxvec = vec[i0]
    if margin == 0:
        avgvec = np.average(vec[0:-1])
    else:
        avgvec = np.average(vec[margin:-margin])
#    print maxvec, avgvec
    i2 = len(vec)-1
    i1 = 0
    for i in range(i0,len(vec)):
#        print (maxvec-vec[i]), (maxvec-avgvec)
        if (maxvec-vec[i]) > (maxvec-avgvec)/1.:
            i2 = i
            break
    for i in range(i0,-1,-1):
        if (maxvec-vec[i]) > (maxvec-avgvec)/1.:
            i1 = i
            break
    return (i1,i2)

def trim(x,y,imin,imax):
    """Removes range from imin to imax from vectors x,y

    Given two (possibly complex) arrays and indices corresponding to a lower and upper edge,
    this function removes the index range between these edges from both input
    arrays

    Parameters
    ----------
    x, y : array_like of complex
        Arrays to be trimmed
    imin, imax : int
        Lower and upper edge of range to be removed (trimmed) from x,y

    Returns
    -------
    (numpy.ndarray, numpy.ndarray)
        Trimmed arrays

    """
    imin = int(imin)
    imax = int(imax)
    print(len(x),len(y))

    def corr(xx):
        xpart1 = xx[0:imin]
        xpart2 = xx[imax:]
        if len(xpart1) == 0:
            xpart1 = xx[0:1]
        if len(xpart2) == 0:
            xpart2 = xx[-1:]
        return xpart1,xpart2
    xnew = np.concatenate(corr(x))
    ynew = np.concatenate(corr(y))

    if len(xnew) < 4 or len(ynew) < 4:
        xnew = np.concatenate([x[0:2],x[-2:]])
        ynew = np.concatenate([y[0:2],y[-2:]])

    #print(xnew,ynew)

    return (xnew,ynew)

def backmodel(x,params):
    """Function for background model.

    Returns the background model values for a given set of parameters and
    frequency values.  Uses parameter object from lmfit.  The background model
    is given by

    .. math:: f_b(\omega)=(a+b\omega+c\omega^2)
        \exp(j(a'+b'\omega)),

    where :math:`a,b,c,a',b'` are real parameters.

    Parameters
    ----------
    x : float or array_like of float
        Frequency values to evaluate the model at
    params : lmfit.Parameters
        Parameters set with which to generate the background

    Returns
    -------
    numpy.complex128 or numpy.ndarray of numpy.complex128
        Background values at frequencies x with model parameters params

    """
    a = params['a'].value
    b = params['b'].value
    c = params['c'].value
    ap = params['ap'].value
    bp = params['bp'].value
    cp = params['cp'].value
    return (a+b*x+c*np.power(x,2.))*np.exp( 1j*(ap+bp*x+cp*np.power(x,2.)) )

def background2min(params, x, data):
    """Background residual

    Computes the residual vector for the background fitting.  Operates on
    complex vectors but returns a real vector with alternating real and imag
    parts

    Parameters
    ----------
    params : lmfit.Parameters
        Model parameters for background generation
    x : float or array_like of float
        Frequency values for background calculation.  backmodel function is
        used.
    data : complex or array_like of complex
        Background values of signal to be compared to generated background at
        frequency values x.

    Returns
    -------
    numpy.ndarray of numpy.float
        Residual values (model value - data value) at values given in x.
        Alternates real and imaginary values

    """
    model = backmodel(x,params)
    res = model - data
    return realimag(res)

def S11theo(frec,params,ftype='A'): # Equation
    """Theoretical response functions of cavities with no background

    Returns the theory values of cavity response functions for a given set of
    parameters for different cavity models.

    Parameters
    ----------
    frec : float or array_like of float
        Frequency values to calculate the response function at
    params : lmfit.Parameters
        Parameter values for calculation
    ftype : {'A','-A','B','-B','X'}, optional
        Model for response function selection.  These are described in Daniel's
        response function document.  The desired model should be found there and
        selected with this parameter.

        The possible models are (CHECK DANIEL'S RESPONSE FUNCTION DOCUMENT):

        - 'A': Reflection cavity with short circuit boundary condition at input port (default selection)
        - '-A': Reflection cavity with open circuit boundary condition at input port (= model A with a minus sign)
        - 'B': Transmission through a side coupled geometry
        - '-B': Same as model B but with a minux sign
        - 'X': Non-standard model (used in a magnetic field sweep)

    Returns
    -------
    numpy.complex128 or numpy.ndarray of numpy.complex128
        Values of theoretical response function at frequencies given in frec

    """
    Qint = params['Qint'].value
    Qext = params['Qext'].value
    f0 = params['f0'].value
    w0 = f0*2*pi
    w = 2*pi*frec
    kint = w0/Qint
    kext = w0/Qext
    dw = w-w0
#    return (kint+2j*dw) / (kext+kint+2j*dw)
    theta = params['theta']
    if ftype == "A":
        return -1.+(2.*kext*np.exp(1j*theta)) / (kext+kint+2j*dw)
    elif ftype== '-A':
        return 1.-(2.*kext*np.exp(1j*theta)) / (kext+kint+2j*dw)
    elif ftype== 'B':
        return -1.+(kext*np.exp(1j*theta)) / (kext+kint+2j*dw)
    elif ftype== '-B':
        return 1.-(kext*np.exp(1j*theta)) / (kext+kint+2j*dw)
    elif ftype== 'X':
        return 1.-(kext*np.exp(1j*theta)) / (kext+kint-2j*dw)


def S11residual(params, frec, data,ftype='A'):
    """Residual for full fit including background

    Calculates the residual for the full signal and background with respect to
    the given background and theory model.

    Parameters
    ----------
    params : lmfit.Parameters
        Parameter values for calculation
    frec : float or array_like of float
        Frequency values to calculate the combined signal and background
        response function at using params
    data : complex or array_like of complex
        Original signal data values at frequencies frec
    ftype : {'A','-A','B','-B','X'}, optional
        Model for theory response function selection.  See S11theo for
        explanation

    Returns
    -------
        Residual values (model value - data value) at values given in x.
        Alternates real and imaginary values

    """
    model = S11full(frec,params,ftype)
    residual = model - data
    return realimag(residual)

def S11full(frec,params,ftype='A'):
    """
    Function for total response from background model and resonator response
    """
    if ftype == 'A' or ftype == 'B':
        model = -S11theo(frec,params,ftype)*backmodel(frec,params)
    elif ftype == '-A' or ftype == '-B' or ftype == 'X':
        model = S11theo(frec,params,ftype)*backmodel(frec,params)
    return model


def fit(frec,S11,ftype='A',fitbackground=True,trimwidth=5.,doplots=False,margin = 51, oldpars=None, refitback = True, reusefitpars = False, fitwidth=None):
    """**MAIN FIT ROUTINE**

    Fits complex data S11 vs frecuency to one of 4 models adjusting for a multiplicative complex background
    It fits the data in three steps.  Firstly it fits the background signal removing a certain window around the detected peak position.
    Then it fits the model times the background to the full data set keeping the background parameters fixed at the fitted values.  Finally it refits all background and
    model parameters once more starting from the previously fitted values.  The fit model is:

    .. math:: \Gamma'(\omega)=(a+b\omega+c\omega^2)\exp(j(a'+b'\omega))\cdot
        \Gamma(\omega,Q_\\textrm{int},Q_\\textrm{ext},\\theta),


    Parameters
    ----------
    frec : array_like
        Array of X values (typically frequency)
    S11 : array_like
        Complex array of Z values (typically S11 data)
    ftype : {'A','B','-A','-B', 'X'}, optional
        Fit model function (A,B,-A,-B, see S11theo for formulas)
    fitbackground : bool, optional
        If "True" will attempt to fit and remove background.  If "False", will use a constant background equal to 1 and fit only model function to data.
    trimwidth : float, optional
        Number of linewidths around resonance (estimated pre-fit) to remove for background only fit.
    doplots : bool, optional
        If "True", shows debugging and intermediate plots
    margin : float, optional
        Smoothing window to apply to signal for initial guess procedures (the fit uses unsmoothed data)
    oldpars : lmfit.Parameters, optional
        Parameter data from previous fit (expects lmfit Parameter object). Used when "refitback" is "False" or "reusefitpars" is "True".
    refitback : bool, optional
        If set to False, does not fit the background but uses parameters provided in "oldpars".  If set to "True", fits background normally
    reusefitpars : bool, optional
        If set to True, uses parameters provided in "oldpars" as initial guess for fit parameters in main model fit (ignored by background fit)
    fitwidth : float, optional
        If set to a numerical value, will trim the signal to a certain number of widths around the resonance for all the fit

    Returns
    -------
    params : lmfit.Parameters
        Fitted parameter values
    freq : numpy.ndarray
        Array of frequency values within the fitted range
    S11: numpy.ndarray
        Array of complex signal values within the fitted range
    finalresult : lmfit.MinimizerResult
        The full minimizer result object (see lmfit documentation for details)

    """
    # Convert frequency and S11 into arrays
    frec = np.array(frec)
    S11 = np.array(S11)

    #Smooth data for initial guesses
    if margin == None or margin == 0: #If no smooting desired, pass None as margin
        margin=0
        sReS11 = S11.real
        sImS11 = S11.imag
        sS11 = np.array( [x+1j*y for x,y in zip(sReS11,sImS11) ] )
    elif type(margin) != int or margin % 2 == 0 or margin <= 3:
        raise ValueError('margin has to be either None, 0, or an odd integer larger than 3')
    else:
        sReS11 = np.array(smooth(S11.real,margin,3))
        sImS11 = np.array(smooth(S11.imag,margin,3))
        sS11 = np.array( [x+1j*y for x,y in zip(sReS11,sImS11) ] )
    #Make smoothed phase vector removing 2pi jumps
    sArgS11 = np.angle(sS11)
    sArgS11 = np.unwrap(sArgS11)
    sdiffang = np.diff(sArgS11)

    #sdiffang = [ x if np.abs(x)<pi else -pi for x in np.diff(np.angle(sS11)) ]
    #Get resonance index from maximum of the derivative of the imaginary part
    #ires = np.argmax(np.abs(np.diff(sImS11)))
    #f0i=frec[ires]

    #Get resonance index from maximum of the derivative of the phase
    avgph =  np.average(sdiffang)
    errvec = [np.power(x-avgph,2.) for x in sdiffang]
    #ires = np.argmax(np.abs(sdiffang[margin:-margin]))+margin
    if margin == 0:
        ires = np.argmax(errvec[0:-1])+0
    else:
        ires = np.argmax(errvec[margin:-margin])+margin
    f0i=frec[ires]
    print("Max index: ",ires," Max frequency: ",f0i)

    if doplots:
        plt.clf()
        plt.title('Original signal (Re,Im)')
        plt.plot(frec,S11.real)
        plt.plot(frec,S11.imag)
        plt.axis('auto')
        plt.show()

        plt.plot(np.angle(sS11))
        plt.title('Smoothed Phase')
        plt.axis('auto')
        plt.show()
        if margin == 0:
            plt.plot(sdiffang[0:-1])
        else:
            plt.plot(sdiffang[margin:-margin])
        plt.plot(sdiffang)
        plt.title('Diff of Smoothed Phase')
        plt.show()

    #Get peak width by finding width of spike in diffphase plot
    (imin,imax) = getwidth_phase(ires,errvec,margin)
    di = imax-imin
    print("Peak limits: ",imin,imax)
    print("Lower edge: ",frec[imin]," Center: ",frec[ires]," Upper edge: ",frec[imax]," Points in width: ", di)

    if doplots:
        plt.title('Smoothed (ph-phavg)\^2')
        plt.plot(errvec)
        plt.plot([imin],[errvec[imin]],'ro')
        plt.plot([imax],[errvec[imax]],'ro')
        plt.show()

    if not fitwidth==None:
        i1 = max(int(ires-di*fitwidth),0)
        i2 = min(int(ires+di*fitwidth),len(frec))
        frec = frec[i1:i2]
        S11 = S11[i1:i2]
        ires = ires - i1
        imin = imin - i1
        imax = imax - i1


    #Trim peak from data (trimwidth times the width)
    (backfrec, backsig) = trim(frec,S11,ires-trimwidth*di,ires+trimwidth*di)


    if doplots:
        plt.title('Trimmed signal for background fit (Re,Im)')
        plt.plot(backfrec,backsig.real,backfrec,backsig.imag)
        plt.plot(frec,S11.real,frec,S11.imag)
        plt.show()

        plt.title('Trimmed signal for background fit (Abs)')
        plt.plot(backfrec,np.abs(backsig))
        plt.plot(frec,np.abs(S11))
        plt.show()

        plt.title('Trimmed signal for background fit (Phase)')
        plt.plot(backfrec,np.angle(backsig))
        plt.plot(frec,np.angle(S11))
        plt.show()


    if fitbackground:
        #Make initial background guesses
        b0 = (np.abs(sS11)[-1] - np.abs(sS11)[0])/(frec[-1]-frec[0])
    #    a0 = np.abs(sS11)[0] - b0*frec[0]
        a0 = np.average(np.abs(sS11)) - b0*backfrec[0]
    #    a0 = np.abs(sS11)[0] - b0*backfrec[0]
        c0 = 0.
    #    bp0 = ( np.angle(sS11[di])-np.angle(sS11[0]) )/(frec[di]-frec[0])
        xx = []
        for i in range(0,len(backfrec)-1):
            df = backfrec[i+1]-backfrec[i]
            dtheta = np.angle(backsig[i+1])-np.angle(backsig[i])
            if (np.abs(dtheta)>pi):
                continue
            xx.append(dtheta/df)
        #Remove infinite values in xx (from repeated frequency points for example)
        xx = np.array(xx)
        idx = np.isfinite(xx)
        xx = xx[idx]

    #    bp0 = np.average([ x if np.abs(x)<pi else 0 for x in np.diff(np.angle(backsig))] )/(frec[1]-frec[0])
        bp0 = np.average(xx)
    #   ap0 = np.angle(sS11[0]) - bp0*frec[0]
    #   ap0 = np.average(np.unwrap(np.angle(backsig))) - bp0*backfrec[0]
        ap0 = np.unwrap(np.angle(backsig))[0] - bp0*backfrec[0]
        cp0 = 0.
        print(a0,b0,ap0,bp0)
    else:
        a0=0
        b0=0
        c0=0
        ap0=0
        bp0=0
        cp0=0

    params = Parameters()
    myvary = True
    params.add('a', value= a0, vary=myvary)
    params.add('b', value= b0, vary=myvary)
    params.add('c', value= c0, vary=myvary)
    params.add('ap', value= ap0, vary=myvary)
    params.add('bp', value= bp0, vary=myvary)
    params.add('cp', value= cp0, vary=myvary)

    if not fitbackground:
        if ftype == 'A' or ftype == 'B':
            params['a'].set(value=-1, vary=False)
        elif ftype == '-A' or ftype == '-B' or ftype == 'X':
            params['a'].set(value=1, vary=False)
        params['b'].set(value=0, vary=False)
        params['c'].set(value=0, vary=False)
        params['ap'].set(value=0, vary=False)
        params['bp'].set(value=0, vary=False)
        params['cp'].set(value=0, vary=False)
    elif not refitback and oldpars != None:
        params['a'].set(value=oldpars['a'].value, vary=False)
        params['b'].set(value=oldpars['b'].value, vary=False)
        params['c'].set(value=oldpars['c'].value, vary=False)
        params['ap'].set(value=oldpars['ap'].value, vary=False)
        params['bp'].set(value=oldpars['bp'].value, vary=False)
        params['cp'].set(value=oldpars['cp'].value, vary=False)

# do background fit

    params['cp'].set(value=0.,vary=False)
    result = minimize(background2min, params, args=(backfrec, backsig))
    '''
    params = result.params
    params['a'].set(vary=False)
    params['b'].set(vary=False)
    params['c'].set(vary=False)
    params['ap'].set(vary=False)
    params['bp'].set(vary=False)
    params['cp'].set(vary=True)
    result = minimize(background2min, params, args=(backfrec, backsig))

    params = result.params
    params['a'].set(vary=True)
    params['b'].set(vary=True)
    params['c'].set(vary=True)
    params['ap'].set(vary=True)
    params['bp'].set(vary=True)
    params['cp'].set(vary=True)
    result = minimize(background2min, params, args=(backfrec, backsig))
    '''

# write error report
    report_fit(result.params)

#calculate final background and remove background from original data
    complexresidual = un_realimag(result.residual)
    backgroundfit = backsig + complexresidual
    fullbackground = np.array([backmodel(xx,result.params) for xx in frec])
    S11corr = -S11 / fullbackground
    if ftype == '-A' or ftype == '-B':
        S11corr = -S11corr

    if doplots:
        plt.title('Signal and fitted background (Re,Im)')
        plt.plot(frec,S11.real)
        plt.plot(frec,S11.imag)
        plt.plot(frec,fullbackground.real)
        plt.plot(frec,fullbackground.imag)
        plt.show()

        plt.title('Signal and fitted background (Phase)')
        plt.plot(frec,np.angle(S11))
        plt.plot(frec,np.angle(fullbackground))
        plt.show()

        plt.title('Signal and fitted background (Polar)')
        plt.plot(S11.real,S11.imag)
        plt.plot(fullbackground.real,fullbackground.imag)
        plt.show()

        plt.title('Signal with background removed (Re,Im)')
        plt.plot(frec,S11corr.real)
        plt.plot(frec,S11corr.imag)
        plt.show()

        plt.title('Signal with background removed (Phase)')
        ph = np.unwrap(np.angle(S11corr))
        plt.plot(frec,ph)
        plt.show()

        plt.title('Signal with background removed (Polar)')
        plt.plot(S11corr.real,S11corr.imag)
        plt.show()


#Make initial guesses for peak fit
#    ires = np.argmax(S11corr.real)
#    f0i=frec[ires]
#    imin = np.argmax(S11corr.imag)
#    imax = np.argmin(S11corr.imag)


    ktot = np.abs(frec[imax]-frec[imin])
    if ftype == 'A':
        Tres = np.abs(S11corr[ires]+1)
        kext0 = ktot*Tres/2.
    elif ftype == '-A':
        Tres = np.abs(1-S11corr[ires])
        kext0 = ktot*Tres/2.
    elif ftype == '-B':
        Tres = np.abs(S11corr[ires])
        kext0 = (1-Tres)*ktot
    elif ftype == 'B':
        Tres = np.abs(S11corr[ires])
        kext0 = (1+Tres)*ktot
    elif ftype == 'X':
        Tres = np.abs(S11corr[ires])
        kext0 = (1-Tres)*ktot
    kint0 = ktot-kext0
    if kint0<= 0.:
        kint0 = kext0
    Qint0 = f0i/kint0
    Qext0 = f0i/kext0

#Make new parameter object (includes previous fitted background values)
    params = result.params
    if reusefitpars and oldpars != None:
        params.add('Qint', value=oldpars['Qint'].value,vary=True,min = 0)
        params.add('Qext', value=oldpars['Qext'].value,vary=True,min = 0)
        params.add('f0', value=oldpars['f0'].value,vary=True)
        params.add('theta', value=oldpars['theta'].value,vary=True)
    else:
        params.add('Qint', value=Qint0,vary=True,min = 0)
        params.add('Qext', value=Qext0,vary=True,min = 0)
        params.add('f0', value=f0i,vary=True)
        params.add('theta', value=0,vary=True)
    params['a'].set(vary=False)
    params['b'].set(vary=False)
    params['c'].set(vary=False)
    params['ap'].set(vary=False)
    params['bp'].set(vary=False)
    params['cp'].set(vary=False)

#Do final fit
    finalresult = minimize(S11residual, params, args=(frec, S11, ftype))
# write error report
    report_fit(finalresult.params)
    params = finalresult.params
    try:
        print('QLoaded = ', 1/(1./params['Qint'].value+1./params['Qext'].value))
    except ZeroDivisionError:
        print('QLoaded = ', 0.)


    if doplots:
        plt.title('Pre-Final signal and fit (Re,Im)')
        plt.plot(frec,S11corr.real)
        plt.plot(frec,S11corr.imag)
        plt.plot(frec,S11theo(frec,params,ftype).real)
        plt.plot(frec,S11theo(frec,params,ftype).imag)
        plt.show()

        plt.title('Pre-Final signal and fit (Polar)')
        plt.plot(S11.real,S11.imag)
        plt.plot(S11full(frec,params,ftype).real,S11full(frec,params,ftype).imag)
        plt.axes().set_aspect('equal', 'datalim')
        plt.show()

#REDO final fit varying all parameters
    if refitback and fitbackground:
        params['a'].set(vary=True)
        params['b'].set(vary=True)
        params['c'].set(vary=True)
        params['ap'].set(vary=True)
        params['bp'].set(vary=True)
        params['cp'].set(vary=False)
        finalresult = minimize(S11residual, params, args=(frec, S11, ftype))

# write error report
        report_fit(finalresult.params)
        params = finalresult.params
        try:
            print('QLoaded = ', 1/(1./params['Qint'].value+1./params['Qext'].value))
        except ZeroDivisionError:
            print('QLoaded = ', 0.)


#calculate final result and background
    complexresidual = un_realimag(finalresult.residual)
    finalfit = S11 + complexresidual
    newbackground = np.array([backmodel(xx,finalresult.params) for xx in frec])

    if doplots:
        plt.title('Final signal and fit (Re,Im)')
        plt.plot(frec,S11.real)
        plt.plot(frec,S11.imag)
        plt.plot(frec,finalfit.real)
        plt.plot(frec,finalfit.imag)
        plt.show()

        plt.title('Final signal and fit (Polar)')
        plt.plot(S11.real,S11.imag)
        plt.plot(finalfit.real,finalfit.imag)
        plt.axes().set_aspect('equal', 'datalim')
        plt.show()

        plt.title('Final signal and fit (Abs)')
        plt.plot(frec,np.abs(S11))
        plt.plot(frec,np.abs(finalfit))
        plt.show()

    chi2 = finalresult.chisqr


    return params,frec,S11,finalresult



def find_resonance(frec,S11,margin=31,doplots=False):
    """Returns the resonance frequency from maximum of the derivative of the phase

    Not currently in use.  Stripped down version of fit
    """
    #Smooth data for initial guesses
    sReS11 = np.array(smooth(S11.real,margin,3))
    sImS11 = np.array(smooth(S11.imag,margin,3))
    sS11 = np.array( [x+1j*y for x,y in zip(sReS11,sImS11) ] )
    #Make smoothed phase vector removing 2pi jumps
    sArgS11 = np.angle(sS11)
    sArgS11 = np.unwrap(sArgS11)
    sdiffang = np.diff(sArgS11)

    #Get resonance index from maximum of the derivative of the phase
    avgph =  np.average(sdiffang)
    errvec = [np.power(x-avgph,2.) for x in sdiffang]
    ires = np.argmax(errvec[margin:-margin])+margin
    f0i=frec[ires]
    print("Max index: ",ires," Max frequency: ",f0i)

    if doplots:
        plt.title('Original signal (Re,Im)')
        plt.plot(frec,S11.real)
        plt.plot(frec,S11.imag)
        plt.show()

        plt.plot(np.angle(sS11))
        plt.title('Smoothed Phase')
        plt.axis('auto')
        plt.show()
        plt.plot(sdiffang[margin:-margin])
        plt.plot(sdiffang)
        plt.title('Diff of Smoothed Phase')
        plt.show()

        plt.title('Smoothed (ph-phavg)\^2')
        plt.plot(errvec)
        plt.plot([ires],[errvec[ires]],'ro')
        plt.show()

    return f0i

def diff_find_resonance(frec,diffS11,margin=31,doplots=False):
    """Returns the resonance frequency from maximum of the derivative of the phase

    Not currently in use.  Stripped down version of fit
    """
    #Smooth data for initial guesses
    sReS11 = np.array(smooth(diffS11.real,margin,3))
    sImS11 = np.array(smooth(diffS11.imag,margin,3))
    sS11 = np.array( [x+1j*y for x,y in zip(sReS11,sImS11) ] )
    #Make smoothed phase vector removing 2pi jumps
    sArgS11 = np.angle(sS11)
    sArgS11 = np.unwrap(sArgS11)
    sdiffang = np.diff(sArgS11)

    #Get resonance index from maximum of the derivative of the phase
    avgph =  np.average(sdiffang)
    errvec = [np.power(x-avgph,2.) for x in sdiffang]
    ires = np.argmax(errvec[margin:-margin])+margin
    f0i=frec[ires]
    print("Max index: ",ires," Max frequency: ",f0i)

    if doplots:
        plt.title('Original signal (Re,Im)')
        plt.plot(frec,diffS11.real)
        plt.plot(frec,diffS11.imag)
        plt.plot(frec,np.abs(diffS11))
        plt.show()

        plt.plot(np.angle(sS11))
        plt.title('Smoothed Phase')
        plt.axis('auto')
        plt.show()
        plt.plot(sdiffang[margin:-margin])
        plt.title('Diff of Smoothed Phase')
        plt.show()

        plt.title('Smoothed (ph-phavg)\^2')
        plt.plot(errvec)
        plt.plot([ires],[errvec[ires]],'ro')
        plt.show()

    return f0i
