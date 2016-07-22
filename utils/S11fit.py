import numpy as np
from scipy.signal import savgol_filter as smooth
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters, Parameter, report_fit
#from smooth import smooth
pi = np.pi

def realimag(array): #Makes alternating real and imaginary part array from complex array
    return np.array([(x.real, x.imag) for x in array]).flatten()
def un_realimag(array): #Makes complex array from alternating real and imaginary part array
    z = []
    for x,y in zip(array[::2],array[1::2]):
        z.append(x+1j*y)
    return np.array(z)

def getwidth(i0,vec): #Unused... Used before when using Imag to find peak width
    f0 = vec[i0]
    i2 = len(vec)-1
    i1 = 0.
    for i in range(i0,len(vec)):
        if f0*vec[i] < 0:
            i2 = i
            break
    for i in range(i0,-1,-1):
        if f0*vec[i] < 0:
            i1 = i
            break
    return (i1,i2)
#Finds indices of peak width of array "vec" assuming "i0" is the peak maximum.  Ignores points within "margin" of the ends
def getwidth_phase(i0,vec,margin):
    maxvec = vec[i0]
    avgvec = np.average(vec[margin:-margin])
#    print maxvec, avgvec
    i2 = len(vec)-1
    i1 = 0.
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

#removes range from imin to imax from vectors x,y
def trim(x,y,imin,imax):
    print len(x),len(y)
    xnew = np.concatenate((x[0:imin],x[imax:]))
    ynew = np.concatenate((y[0:imin],y[imax:]))
    return (xnew,ynew)

#Function for background model.  Uses parameter object from lmfit
def backmodel(x,params):
    a = params['a'].value
    b = params['b'].value
    c = params['c'].value
    ap = params['ap'].value
    bp = params['bp'].value
    cp = params['cp'].value
    return (a+b*x+c*np.power(x,2.))*np.exp( 1j*(ap+bp*x+cp*np.power(x,2.)) )

#Complex residual of for the background fit
def background2min(params, x, data):
    model = backmodel(x,params)
    res = model - data
    return realimag(res)

#Response function for resonator. Uses parameter object from lmfit
def S11theo(frec,params,ftype='A'): # Equation 
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

#Residual for full fit including background
def S11residual(params, frec, data,ftype='A'):
    model = -S11theo(frec,params,ftype='A')*backmodel(frec,params)
    residual = model - data
    return realimag(residual)

#Function for total response from background model and resonator response
def S11full(frec,params,ftype='A'):
    model = -S11theo(frec,params,ftype='A')*backmodel(frec,params)
    return model

def fit(frec,S11,fitbackground=True,trimwidth=5.,doplots=False,margin = 51, oldpars=None, refitback = True, reusefitpars = False):

    #Smooth data for initial guesses
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
    ires = np.argmax(errvec[margin:-margin])+margin
    f0i=frec[ires]
    print "Max index: ",ires," Max frequency: ",f0i

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

    #Get peak width by finding width of spike in diffphase plot
    (imin,imax) = getwidth_phase(ires,errvec,margin)
    di = imax-imin
    print "Peak limits: ",imin,imax
    print "Lower edge: ",frec[imin]," Center: ",frec[ires]," Upper edge: ",frec[imax]," Points in width: ", di

    if doplots:
        plt.title('Smoothed (ph-phavg)\^2')
        plt.plot(errvec)
        plt.plot([imin],[errvec[imin]],'ro')
        plt.plot([imax],[errvec[imax]],'ro') 
        plt.show()

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



    #Make initial background guesses
    b0 = (np.abs(sS11)[-1] - np.abs(sS11)[0])/(frec[-1]-frec[0])
    a0 = np.abs(sS11)[0] - b0*frec[0]
    c0 = 0.
#    bp0 = ( np.angle(sS11[di])-np.angle(sS11[0]) )/(frec[di]-frec[0])
    xx = []
    for i in range(0,len(backfrec)-1):
        df = backfrec[i+1]-backfrec[i]
        dtheta = np.angle(backsig[i+1])-np.angle(backsig[i])
        if (np.abs(dtheta)>pi):
            continue
        xx.append(dtheta/df)
#    bp0 = np.average([ x if np.abs(x)<pi else 0 for x in np.diff(np.angle(backsig))] )/(frec[1]-frec[0])
    bp0 = np.average(xx)
    ap0 = np.angle(sS11[0]) - bp0*frec[0]
    cp0 = 0.
    print a0,b0,ap0,bp0

    params = Parameters()
    myvary = True
    params.add('a', value= a0, vary=myvary)
    params.add('b', value= b0, vary=myvary)
    params.add('c', value= c0, vary=myvary)
    params.add('ap', value= ap0, vary=myvary)
    params.add('bp', value= bp0, vary=myvary)
    params.add('cp', value= cp0, vary=myvary)

    if not fitbackground:
        params['a'].set(value=-1, vary=False)
        params['b'].set(value=0, vary=False)
        params['c'].set(value=0, vary=False)
        params['ap'].set(value=0, vary=False)
        params['bp'].set(value=0, vary=False)
        params['cp'].set(value=0, vary=False)
    elif not refitback:
        params['a'].set(value=oldpars['a'].value, vary=False)
        params['b'].set(value=oldpars['b'].value, vary=False)
        params['c'].set(value=oldpars['c'].value, vary=False)
        params['ap'].set(value=oldpars['ap'].value, vary=False)
        params['bp'].set(value=oldpars['bp'].value, vary=False)
        params['cp'].set(value=oldpars['cp'].value, vary=False)

# do background fit
    result = minimize(background2min, params, args=(backfrec, backsig))

# write error report
    report_fit(result.params)

#calculate final background and remove background from original data
    complexresidual = un_realimag(result.residual)
    backgroundfit = backsig + complexresidual
    fullbackground = np.array([backmodel(xx,result.params) for xx in frec])
    S11corr = -S11 / fullbackground

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
 
        plt.title('Signal with background removed (Polar)')
        plt.plot(S11corr.real,S11corr.imag)
        plt.show()


#Make initial guesses for peak fit
    ires = np.argmax(S11corr.real)
    f0i=frec[ires]
    imin = np.argmax(S11corr.imag)
    imax = np.argmin(S11corr.imag)

    ktot = np.abs(frec[imax]-frec[imin])
    Tres = np.abs(S11corr[ires]+1)
    kext0 = ktot*Tres/2.
    kint0 = ktot-kext0

    Qint0 = f0i/kint0
    Qext0 = f0i/kext0

#Make new parameter object (includes previous fitted background values)
    params = result.params
    if not reusefitpars:
        params.add('Qint', value=Qint0,vary=True)
        params.add('Qext', value=Qext0,vary=True)
        params.add('f0', value=f0i,vary=True)
        params.add('theta', value=0,vary=True)
    else:
        params.add('Qint', value=oldpars['Qint'].value,vary=True)
        params.add('Qext', value=oldpars['Qext'].value,vary=True)
        params.add('f0', value=oldpars['f0'].value,vary=True)
        params.add('theta', value=oldpars['theta'].value,vary=True)
    params['a'].set(vary=False)
    params['b'].set(vary=False)
    params['c'].set(vary=False)
    params['ap'].set(vary=False)
    params['bp'].set(vary=False)
    params['cp'].set(vary=False)

#Do final fit
    finalresult = minimize(S11residual, params, args=(frec, S11))
# write error report
    report_fit(finalresult.params)
    params = finalresult.params
    print 'QLoaded = ', 1/(1./params['Qint'].value+1./params['Qext'].value)

#REDO final fit varying all parameters
    if refitback:
        params['a'].set(vary=True)
        params['b'].set(vary=True)
        params['c'].set(vary=True)
        params['ap'].set(vary=True)
        params['bp'].set(vary=True)
        params['cp'].set(vary=True)
        finalresult = minimize(S11residual, params, args=(frec, S11))

# write error report
        report_fit(finalresult.params)
        params = finalresult.params
        print 'QLoaded = ', 1/(1./params['Qint'].value+1./params['Qext'].value)


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


    return params

