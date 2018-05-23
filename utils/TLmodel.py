import numpy as np
import scipy.constants as const
from scipy.optimize import minimize
from scipy.optimize import brentq
import copy

def S11theo(f,f0,kint,kext):
    df = f-f0
    return -1.+(2.*kext) / (kext+kint+2j*df)

def S11(Zin,params):
    Z0p = params['Z0p']
    result = (Zin-Z0p)/(Zin+Z0p)
    return result

def Zincircuit(omega,params):
    l = params['l']
    Z0 = params['Z0']
    vph = const.c/params['n']
    beta = omega/vph
    al = alpha(omega,params)
    gamma = al+1j*beta
    Zin = Zload(omega,params)
    Zin = ZTL(Z0,Zin,gamma*l)
    Zc = Zcoup(omega,params)
    Zin = Zparallel(Zin,Zc)
    return Zin


def Zincircuit_approx(omega,params):
    l = params['l']
    Z0 = params['Z0']
    al = alpha(omega,params)
    Zc = Zcoup(omega,params)
    vph = const.c/params['n']
    if params['type'] == 'lambda/2':
        lj = params['Lg']/(Z0/vph)
        w0u = np.pi*vph/(l+lj)
        Ll = Z0*np.pi/2/w0u
        Cl = 2/np.pi/Z0/w0u
    elif params['type'] == 'lambda/4':
        lj = 0
        w0u = np.pi*vph/2/(l+lj)
        Ll = Z0*np.pi/4/w0u
        Cl = 4/np.pi/Z0/w0u
    Rl = Z0*al*l
    Zin = Rl + 1j*omega*Ll + 1/(1j*omega*Cl)
    Zc = Zcoup(omega,params)
    Zin = Zparallel(Zin,Zc)
    return Zin

def ZTL(Z0,Zl,gammal):
    result = Z0*(Zl+Z0*np.tanh(gammal))/(Z0+Zl*np.tanh(gammal))
    return result

def Zcoup(omega,params):
    C = params['Cs']
    return 1/(1j*omega*C)

def Zload(omega,params):
    L = params['Lg']
    Z = 1j*omega*L
    if 'Lj' in params:
        Lj = params['Lj']
        Cj = params['Cj']
        Rj = params['Rj']
        Zj = (1j*Lj*Rj*omega)/(Rj + 1j*Lj*omega - Cj*Lj*Rj*omega**2.)
        Z += Zj
    if 'Cg' in params:
        Cg = params['Cg']
        if Cg is not 0:
            Z = Zparallel(Z,1/(1j*omega*Cg))
    return Z

def Zparallel(*args):
    result = 0
    for z in args:
        result += 1/z
    result = 1/result
    return result

def Vin(omega,params): #V0 is the incoming wave amplitude
    if 'Pin' in params:
        V0 = PintoV0(params)
    else:
        V0 = 1
    result = V0*(1+S11(Zincircuit(omega,params),params))
    return result

def Vx(x,omega,params): #Voltage along TL.  x counts from the load (at 0) to l (at input)
    l = params['l']
    Z0 = params['Z0']
    vph = const.c/params['n']
    beta = omega/vph
    al = alpha(omega,params)
    gamma = al+1j*beta
    GammaL = (Zload(omega,params)-Z0)/(Zload(omega,params)+Z0)
    result = Vin(omega,params)/(np.exp(gamma*l) + GammaL*np.exp(-gamma*l) )*(np.exp(gamma*x) + GammaL*np.exp(-gamma*x) )
    return result

def omega0(params,wws=None): #Range wws in rad/sec
    if wws is None: #Default to 2Ghz to 10Ghz search range
        ffs= np.linspace(2,10,5001)*1e9
        wws= 2.*np.pi*ffs
    else:
        ffs = wws/2/np.pi

    i0 = np.argmax(np.power(np.diff(np.imag(Zincircuit(wws,params))),2.)) #find derivative maximum
    fres = ffs[i0]
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

def f0(params,ffs=None): #Range ffs in Hz
    if ffs is None: #Default to 2Ghz to 10Ghz search range
        ffs= np.linspace(2,10,5001)*1e9
        wws= 2.*np.pi*ffs
    else:
        wws = ffs*2*np.pi
    return omega0(params,wws)/2/np.pi

def Zx(x,omega,params): #Z along TL.  x counts from the load (at 0) to l (at input)
    l = params['l']
    Z0 = params['Z0']
    vph = const.c/params['n']
    beta = omega/vph
    al = alpha(omega,params)
    gamma = al+1j*beta
    Zl = Zload(omega,params)
    result = Z0*(Zl+1j*Z0*np.tan(-1j*gamma*x))/(Z0+1j*Zl*np.tan(-1j*gamma*x))
    return result

def PintoV0(params):
    Plin = np.power(10,params['Pin']/10)*1e-3
    return np.sqrt(2.*params['Z0p']*Plin)

def Ix(x,omega,params): #Current along TL
    return Vx(x,omega,params)/Zx(x,omega,params)

def Vj(omega,params): #If there is a Lj and Cg in params, returns the voltage accross the junction (complex).  Else, just the load voltage
    Vl = Vx(0,omega,params)
    if 'Lj' in params:
        Zl = Zload(omega,params)
        if 'Cg' in params:
            Zl0 = 1/(1j*omega*params['Cg'])*Zl/(1/(1j*omega*params['Cg'])-Zl)
            Ij = Vl/Zl0
        else:
            Ij = Vl/Zl
        result = Vl-Ij*1j*omega*params['Lg']
        return result
    else:
        return Vl

def Ij(omega,params): #If there is a Lj in params, returns the voltage accross the junction (complex).  Else, just the load voltage
    Vl = Vx(0,omega,params)
    Zl = Zload(omega,params)
    Il = Vl/Zl
    return Il

def alpha(omega,params):
    return params['alpha']

def FindParFromRes(params,w0,a,b,par='Lj',wws=None): #Finds approximate value of par to have a resonance frequency of w0 (angular).  a,b is the bracketing interval

    newparams = copy.deepcopy(params)
    def myfunc(x,w0,par,params,wws=None):
        newparams[par] = x
        result = omega0(params,wws)
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
    par0 = brentq(myfunc,a,b,args=(w0,par,newparams,wws)) #Find root
    return par0
    

if __name__ == "__main__":


    #Readjusted values
    params = {'Z0': 64.611, 'Cj': 1.77e-15, 'Z0p': 79.400384766937506, 'Lg': 1.0432952403781536e-10, 'Rj': 1027.6618763504205, 'n': 2.876042565429968, 'type': 'lambda/2', 'alpha': 0.0060728306929787035, 'Lj': 2.0916766016363636e-10, 'Pin': -122, 'Cs': 2.657e-11, 'l': 0.006119}
    wres = 49685604684.2

    a=0
    b=1e-9

    result = FindParFromRes(params,wres,a,b,par='Lj',wws=None)
    print(result)












