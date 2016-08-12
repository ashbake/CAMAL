# Run stuff
# for mag stuff: https://www.astro.umd.edu/~ssm/ASTR620/mags.html#flux

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapz
import sys
plt.ion()

sys.path.append("../")
from tools import toolbox
from tools import camal as cm

lf = toolbox.loadfile()
tl = toolbox.tools()

from loadSpec import loadspec


# Load Fake star field
V, J, T = lf.trilegal('../inputs/TRILEGAL/fakestarsout_VJ.dat')

# Load Tapas (need new tapas that covers 685-1100)
xtap, ytap             = lf.tapas('../inputs/TAPAS/tapas_600nm_1150nm_H2O.txt')
xray, yray             = lf.tapas('../inputs/TAPAS/tapas_600nm_1150nm_rayleigh.txt')
cv                     = 9.526 # milimeters, from tapas header, email correspondence confirmed mm units

print 'Loaded Fake star field and TAPAS'

## Load Synthetic Stellar Field & Find Mearth fluxes (photons/sec/cm2)
## normalizing spectrum according to J.. Skip Teffs not in PHOENIX
## -------------------------------------------------------------------
MEphot_exp = []
MEphot_5mm = []
MEphot_10mm = []
ME5_noise   = [] 
ME10_noise = []

for i,temps in enumerate(T):

    # Apply limits of Phoenix models
    if temps > 400.0 and temps < 70000:

        # Inputs to loadspec need to be integers, temp rounded to 2 sig figs
        xtemp, ytemp = loadspec(int(np.round(temps,-2)), 2, 0)

        # Load Filter profiles if don't exist
        try:
            J_filt
        except NameError:
            J_filt     = lf.filters(['../inputs/FILTERS/J.txt'],xtemp/10000)[0]
            ME_filt    = lf.filters(['../inputs/FILTERS/mearth_ccd.dat'],xtemp)[0]
            ytap_1     = tl.interp(xtemp, xtap[::-1]*10, np.abs(ytap[::-1])**(0.5/cv)) #tau = PWV_new/cv
            yray_1     = tl.interp(xtemp, xray[::-1]*10, yray[::-1])
            print "Loaded Filter Profiles interpolated at PHOENIX Wavelength points"

        # Determine Calibration J in photons/sec/cm^2 (expected/raw)
        Jphot_raw   =    tl.integrate(xtemp,ytemp * J_filt)
        Jphot_exp   =    (1600/0.16) * 1.5E7 * 10**(-0.4 * J[i])
        
        # Get the Expected MEarth flux
        MEphot_exp.append(tl.integrate(xtemp,(Jphot_exp/Jphot_raw) * ytemp * 
                                   ME_filt * ytap_1**(0.5/cv) * yray_1))
        MEphot_5mm.append(tl.integrate(xtemp,(Jphot_exp/Jphot_raw) * ytemp *
                                   ME_filt * ytap_1**(5.0/cv) * yray_1))
        MEphot_10mm.append(tl.integrate(xtemp,(Jphot_exp/Jphot_raw) * ytemp *
                                   ME_filt * ytap_1**(10.0/cv) * yray_1))
        
        # Add noise to 5mm case
        ME5_noise 

# plt.plot(T[np.where(T < 100000)],-2.5*np.log10(np.array(MEphot_exp)/np.array(MEphot_10mm)),'go')


def getfakes(tau):
    """ Multiply telescope efficiency, synthetic spectrum, 
     water absorption spectrum, integrate filters, then
     multiply by CCD efficiency. 0.95 is from 670 high pass filter"""
    trans_t = tel_eff * yphoe * ytap**tau
    f1 = 0.32 * .95 * tl.integrate(xtap,filters[0]*0.01* trans_t)
    f2 = 0.26 * tl.integrate(xtap,filters[1]*0.01* trans_t)
    f3 = 0.19 *a * tl.integrate(xtap,filters[2]*0.01* trans_t)
    return f2/f1, f3/f1



