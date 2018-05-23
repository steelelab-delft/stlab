import numpy as np
import copy
import scipy.constants as const
from scipy.integrate import odeint
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

phi0 = const.value('mag. flux quantum')


def smoothclamp(x, mi, mx): return mi + (mx-mi)*(lambda t: np.where(t < 0 , 0, np.where( t <= 1 , 3*t**2-2*t**3, 1 ) ) )( (x-mi)/(mx-mi) )

#def odefunc(z,t,sclass,Infunc,fpars):
#    return JJ_solver.JJeqn_model(sclass,z,t,Infunc,fpars)

#required params form params = {'Ic':Ic, 'Rsg': Rsg, 'Rn':Rn, 'Vgap':Vgap, 'Cj':Cj, 'R0':R0, 'Rm':Rm, 'R1':R1}        
class JJ_solver:
    def setup(self,params):
        for lab,val in params.items():
            setattr(self,lab,val)
        if self.R1==np.infty:
            self.Rth = self.Rm + self.R0
        else:        
            self.Rth = self.Rm + self.R0*self.R1/(self.R0+self.R1)
        self.wp = np.sqrt(2*np.pi*self.Ic/phi0/self.Cj)
    def __init__(self,params):
        self.setup(params)
    def R(self,V):
        result = (-smoothclamp(V/self.Vgap,0.99,1)+1)/0.01*(self.Rsg-self.Rn)+self.Rn  #Smoothly goes from Rsg to Rn over the voltage range 0.99*Vgap to 1*Vgap
        return result
    def Reff(self,V):  #Final effective voltage (parallel of Rth and R)
        return self.R(V)*self.Rth/(self.R(V)+self.Rth)
    def Q(self,V):  #Final effective Qfactor
        result = self.wp*self.Reff(V)*self.Cj
        return result
        
    # for odeint.  Idict is a dictionary required by Ifunc
    def JJeqn_model(self,z,t,Ifunc,Idict):
        f = z[0]
        g = z[1]
        V = phi0/2/np.pi*g*self.wp
        fp = g
        gp = Ifunc(t/self.wp,Idict)/self.Ic-(1/self.Q(V)*g+np.sin(f))
        return np.array([fp,gp])

    def solve(self, ts, Ifunc, Idict, init0=[0,0]):  #Standard time variable
#        print(tuple([Infunc, kwargs]))
#        print(self.wp)
        taus = ts*self.wp
        sols = odeint(self.JJeqn_model, init0, taus, args = (Ifunc, Idict) )
        sols = np.insert(sols,0,ts,axis=1)
        sols = sols.T
        self.sol = sols
        self.Icooper = np.sin(self.sol[1])*self.Ic #Cooper pair current (in amps)
        self.Vj = phi0/2/np.pi*self.sol[2]*self.wp #Time voltage on junction (in volts)
        if self.R1 == np.infty:
            self.Vfunc = self.Rth * Ifunc(ts,Idict)  #Effecive voltage source function from Ifunc (in volts)
            self.Ij = (self.Vfunc - self.Vj)/(self.Rm+self.R0) #Current through RCSJ (through Rm) junction in amps
            self.I1 = 0.*self.Vfunc
            self.I0 = self.Ij #Source current in amps
        else:
            self.Vfunc = (self.R1+self.R0)*self.Rth/self.R1 * Ifunc(ts,Idict)  #Effecive voltage source function from Ifunc (in volts)
            self.Ij = (self.R1*self.Vfunc - (self.R0+self.R1)*self.Vj)/(self.R1*self.Rm+self.R0*(self.R1+self.Rm)) #Current through RCSJ (through Rm) junction in amps
            self.I1 = (self.Rm*self.Vfunc + self.R0*self.Vj)/(self.R1*self.Rm+self.R0*(self.R1+self.Rm)) #Current through R1 shunt in amps
            self.I0 = ((self.Rm+self.R1)*self.Vfunc - self.R1*self.Vj)/(self.R1*self.Rm+self.R0*(self.R1+self.Rm)) #Source current in amps
        return self.sol

    def solveIV(self,Ivals):
        def Ifunc(t,Idict):
            return Idict['I0']
        Ins = Ivals/self.Ic
        Is = []
        Vs = []
        Ijs = []
        for i,ii in enumerate(Ins):
            Idict = {'I0':self.Ic*ii}
            if i==0:
                dphi0 = 0
                phi00 = 0
            else:
                phi00 = self.sol[1][-1]
                dphi0 = self.sol[2][-1]
            if Idict['I0']>self.Ic:
                tscale = phi0/self.Reff(0)/np.sqrt(Idict['I0']**2-self.Ic**2)
                #print(tscale)
                tscale *= 50
            else:
                if self.Q(0) >= 0.5:
                    tscale = self.Reff(0)*self.Cj
                else:
                    Q = self.Q(0)
                    lmd = 1/2/Q - np.sqrt(1/4/Q**2-1)
                    tscale = 1/lmd/self.wp
                print(tscale)
                tscale *= 100
            ts = np.linspace(0,tscale,20001)
            sols = self.solve(ts,init0=[phi00,dphi0],Idict=Idict,Ifunc=Ifunc) #solve for given time values
            plt.clf()
            plt.plot(ts/self.Trc(0),self.Vj)
            plt.show()
            Vs.append(np.average(self.Vj[5000:]))
            Ijs.append(np.average(self.Ij[5000:]))
        Vs = np.array(Vs)
        Ijs = np.array(Ijs)
        return Ivals,Ijs,Vs


    def Trc(self,V):
        return self.Cj*self.Reff(V)


