# Load Everything need for fitting CAMAL data
# for use in all the codes

# ------- #
# Imports #
# ------- #

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapz
import sys

sys.path.append('../tools/')
import toolbox
import camal as cm

lf = toolbox.loadfile()
tl = toolbox.tools()
plt.ion()

sys.path.append('../fitMearth/')
from loadSpec import loadspec

def getpt(y780,y823,y860):
    slope = (y780 - y860)/(780.-860.)
    point = slope*(823.-780.)+y780
    df = y823 - point
    return slope,df

# ---------------
# Load CAMAL data
# ---------------
#stars = ['polaris1','polaris2','polaris3','regulus','arcturus','altair']#,'spica']
temps = 6000 #[6000 , 6000 , 12500, 4300, 7000]#, 22000]
datafile = '../inputs/CAMAL/finalData_061216_polaris.fits'
#        '../inputs/CAMAL/finalData_061116_polaris.fits',
#        '../inputs/CAMAL/finalData_061416_polaris.fits',
#        '../inputs/CAMAL/finalData_052316_regulus.fits',
#        '../inputs/CAMAL/finalData_052316_arcturus.fits',
#        '../inputs/CAMAL/finalData_052316_altair.fits']#,
#        '../inputs/CAMAL/finalData_052316_spica.fits']


# Load Camal Data
f780, f823, f860, time = lf.camal(datafile)
y                      = [f823/f780, f860/f780]
# Define median & sigma for time series
ys                     = [np.median(y[0]), np.median(y[1])]
yserr                  = [np.std(y[0]), np.std(y[1])]
# Calculate df_823
ref                    = np.median(f780)
slopes_t, dfs_t        = getpt(f780/ref,f823/ref,f860/ref)
slopes,dfs             = np.median(slopes_t), np.median(dfs_t)



# ----------------#
# LOAD DATA STUFF #
# ----------------#

# Load GPS PWV Monitoring data
tGPS, PWV, PWVerr     = lf.suominet('../inputs/amado_PWV.txt')

# Load TAPAS spectrum
xtap, ytap             = lf.tapas('../inputs/TAPAS/tapas_600nm_1150nm_H2O.txt')
xtap = xtap[::-1]
ytap = ytap[::-1]
xray, yray             = lf.tapas('../inputs/TAPAS/tapas_600nm_1150nm_rayleigh.txt')
xray = xray[::-1]
yray = yray[::-1]
cv                     = 9.526 # milimeters, from tapas header, email correspondence confirmed mm units

# Load filter profiles
filters                = lf.filters(['../inputs/FILTERS/780.txt'] , xtap)
filters.append(3.1*cm.gaussian(xtap, 823.1, 3.2/2.355)*100)  # spec sheet: 91.422% max
filters.append(1.73*cm.gaussian(xtap, 860.3, 1.9/2.355)*100)  # spec sheet: 85.439% max

# Telescope eff
f         =  np.loadtxt('../inputs/telescope_efficiency.txt',delimiter=',')
tel_eff   =  tl.interp(xtap, f[:,0],f[:,1])

# Spectrum
temps   = 6000
loggs   = 4.5
FeHs    = 0.0
xtemp, ytemp = loadspec(int(np.round(temps,-2)), loggs, FeHs)
isort   = np.argsort(xtemp)
yspec   = tl.interp(xtap,xtemp[isort]/10.0, ytemp[isort])

def getfakes(PWV,yspec):
    trans_t = tel_eff * yspec * yray**airmass * np.abs(ytap)**(PWV/cv)
    f1 = 0.32 * .95 * tl.integrate(xtap,filters[0]* trans_t) # numbers are ccd efficiency
    f2 = 0.26 * tl.integrate(xtap,filters[1]* trans_t)
    f3 = 0.19 * tl.integrate(xtap,filters[2]* trans_t)
    return f1,f2,f3




