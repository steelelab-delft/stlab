import stlab
from lmfit.models import LorentzianModel,ConstantModel
lorentzian_model = LorentzianModel()+ConstantModel()
from lmfit import Parameters
from copy import deepcopy
from matplotlib import pyplot as plt
import numpy as np
from os.path import join, dirname, basename
import os
import time
from shutil import copyfile

class StarkShifter():
    def __init__(self, pump, f0, f_target, P_initial,max_delta_P_per_hour, averages,
        pna,P_high,P,ifbw,f_start,f_stop,f_points):

        ## Variables
        self.i_fit = 0
        self.pump = pump
        self.f0 = f0
        self.f_target = f_target
        self.P_stark = [P_initial]
        self.max_delta_P_per_hour = max_delta_P_per_hour
        self.averages = averages
        self.f_list = []
        self.data_0 = None
        self.t_P_update = None

        # PNA setting function for calibration
        self.pna = pna
        self.pna_set_cal = lambda:self.set_pna(P_high,ifbw,f_start,f_stop,f_points)
        # PNA setting function for measuring
        self.pna_set = lambda:self.set_pna(P,ifbw,f_start,f_stop,f_points)
        self.f_start = f_start
        self.f_stop = f_stop
        

        # Initialize pump
        self.pump.EXTref()
        self.pump.RFon()
        self.pump.setCWfrequency(7e9)
        self.pump.setCWpower(self.P_stark[-1])
        self.pump.ALCmode('ON')

    def set_pna(self,P,ifbw,f_start,f_stop,f_points):
        self.pna.SetRange(f_start,f_stop)
        self.pna.SetPoints(f_points)
        self.pna.SetIFBW(ifbw)
        self.pna.SetPower(P)

    def dBm_to_mW(self,dBm):
        return np.power(10, dBm/10)

    def mW_to_dBm(self,mW):
        return 10*np.log10(mW)

    def P_target(self,f):
        P = self.dBm_to_mW(self.P_stark[-1])
        alpha_1 = (f-self.f0)/P
        delta = self.f_target-f
        return self.mW_to_dBm(delta/alpha_1 + P)

    def measure_background(self):
        self.pna_set_cal()
        self.data_0 = self.pna.MeasureScreen() 
        self.pna.AutoScaleAll()

        self.myfile= stlab.newfile('stark','',
            self.data_0.keys(), 
            autoindex=True,
            git_id=False)

        # Make folder which will host fits
        folder = dirname(self.myfile.name)
        os.mkdir(join(folder,'fits'))
        copyfile(__file__, join(folder,basename(__file__)))

    def get_frequency(self,data):
        # Fit calibration trace and extract frequency
        x = data['Frequency (Hz)']
        y = 1-10**((data['S21dB (dB)']-(self.data_0['S21dB (dB)']))/20)
        params = Parameters()
        params.add_many(('c', 0.2, True, -5, +5, None, None),
                    ('sigma', 3e6, True, 1e6, 10e6, None, None),
                 ('center', self.f_target, True, self.f_start,self.f_stop, None, None),
                 ('amplitude', 953893, True, 0, None, None, None))
        fit_result = lorentzian_model.fit(params=params, x=x, data=y)
        print(fit_result.fit_report())
        self.fig_latest_fit, ax = plt.subplots(figsize=(5,4))
        fit_result.plot_fit(ax=ax)
        plt.close()
        return fit_result.params['center']

    def get_next_power(self,f):
        P_next = self.P_target(f)
        if self.t_P_update is not None:
            dt = (time.time()-self.t_P_update)/3600 # in hours
            max_dP = self.max_delta_P_per_hour*dt
            dP = P_next - self.P_stark[-1]
            if abs(dP)>abs(max_dP):
                P_next = self.P_stark[-1]+max_dP*np.sign(dP)
        self.t_P_update = time.time()
        return P_next

    def save(self,data):
        folder = dirname(self.myfile.name)
        stlab.savedict(self.myfile, data)
        stlab.metagen.fromarrays(self.myfile,data['Frequency (Hz)'],list(range(len(self.f_list)+1)),xtitle='Frequency (Hz)',ytitle='Iterations',colnames=data.keys())
        np.savetxt(join(folder,'f1_list.txt'),self.f_list)
        np.savetxt(join(folder,'P_list.txt'),self.P_stark)
        self.fig_latest_fit.savefig(fname=join(folder,join('fits','fit_%d' %self.i_fit)))
        self.i_fit += 1

        # Save a plot of all the changes made in power
        fig, ax = plt.subplots(figsize=(5,4))
        plt.plot(self.P_stark[1:])
        fig.savefig(fname=join(folder,'P_stark'))
        plt.close()

        # Save a plot of all the frequencies measured
        fig, ax = plt.subplots(figsize=(5,4))
        plt.plot(self.f_list)
        fig.savefig(fname=join(folder,'f_stark'))
        plt.close()

    def set_power(self):

        if self.data_0 is None:
            self.measure_background()
            self.max_delta_P_per_hour *= 10
            for i in range(self.averages-1):
                self.set_power()
            self.max_delta_P_per_hour /= 10

        self.pna_set()
        data = self.pna.MeasureScreen() #Trigger 2 port measurement and retrieve data in Re,Im format.  Returns OrderedDict
        self.pna.AutoScaleAll()

        f = self.get_frequency(data)
        self.f_list.append(f)

        # Set new power
        P_next = self.get_next_power(np.average(np.array(self.f_list)[-self.averages:]))
        self.P_stark.append(P_next)
        self.pump.setCWpower(self.P_stark[-1])

        # Save stuff
        self.save(data)
