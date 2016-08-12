# Run stuff

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

# Load Tapas
xtap, ytap             = lf.tapas('../inputs/tapas_h2o.txt')

# Load Synthetic Spectrum
filename  = '../inputs/te06000-2.00+0.5.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits'
wave0     =  700.0 # nm
wave1     =  2500.0 # nm
xph, yph  =  lf.phoenix(filename,wave0,wave1,convolve = False)
yphoe     =  tl.interp(xtap, xph, yph)


# Load Filters interpolated at xtapas
filters                = lf.filters(['../inputs/filt_780nm.txt' ,
                                     '../inputs/filt_823nm.txt' ,
                                     '../inputs/filt_860nm.txt'], xtap)

# test replace 860 with narrower gaussian..was told FWHM=2 not 2.4 in email from Kirk
filters[2] = 1.5 * cm.gaussian(xtap, 860.0, 2.0/2.355)

# Load and interpolate telescope throughput curve
f         =  np.loadtxt('../inputs/telescope_efficiency.txt',delimiter=',')
tel_eff   =  tl.interp(xtap, f[:,0],f[:,1])

def getfakes(tau):
    """ Multiply telescope efficiency, synthetic spectrum, 
     water absorption spectrum, integrate filters, then
     multiply by CCD efficiency. 0.95 is from 670 high pass filter"""
    trans_t = tel_eff * yphoe * ytap**tau
    f1 = 0.32 * .95 * tl.integrate(xtap,filters[0]*0.01* trans_t)
    f2 = 0.26 * tl.integrate(xtap,filters[1]*0.01* trans_t)
    f3 = 0.19 *a * tl.integrate(xtap,filters[2]*0.01* trans_t)
    return f2/f1, f3/f1



# Get 2MASS band passes..in microns so divide xph by 1000
filts_2MASS     = lf.filters(['../inputs/J.txt', '../inputs/H.txt', '../inputs/Ks.txt'], xph/1000.)

JHK = np.zeros(3)
for i in range(0,3):
    JHK[i] = tl.integrate(xph, yph * filts_2MASS[i])
    #plt.plot(xph,yph * filts_2MASS[i])

print 'J - K = %s' %(np.round(np.log10(JHK[1]/JHK[2]),3))

