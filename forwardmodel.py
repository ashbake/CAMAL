# Load CAMAL Data, Run forward model for same 

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
# Note 6/14 had low PWV & spica weird
# Put this into configuration file?
# ---------------
stars = ['polaris1','polaris2','polaris3','regulus','arcturus','altair']#,'spica']
temps = [6000,6000 , 6000 , 12500, 4300, 7000]#, 22000]
cols  = ['ro','go','ko','bo','mo','yo']#,'co']
data = ['../inputs/CAMAL/finalData_061216_polaris.fits',
        '../inputs/CAMAL/finalData_061116_polaris.fits',
        '../inputs/CAMAL/finalData_061416_polaris.fits',
        '../inputs/CAMAL/finalData_052316_regulus.fits',
        '../inputs/CAMAL/finalData_052316_arcturus.fits',
        '../inputs/CAMAL/finalData_052316_altair.fits']#,
#        '../inputs/CAMAL/finalData_052316_spica.fits']



# ---------------------------------- #
# Load CAMAL Data & Calculate df_823 #
# ---------------------------------- #
print 'Loading CAMAL data'
dfs    = np.zeros(len(stars))
slopes = np.zeros(len(stars))
ys     = np.zeros((len(stars),2))
yserr  = np.zeros((len(stars),2))

plt.figure()
for i in np.arange(len(data)):
    # Load Camal Data
    f780, f823, f860, time = lf.camal(data[i])
    y = [f823/f780, f860/f780]
    # Define median & sigma for time series
    ys[i]    = np.median(y[0]), np.median(y[1])
    yserr[i] = np.std(y[0]), np.std(y[1])
    # Calculate df_823
    ref = np.median(f780)
    slopes_t, dfs_t = getpt(f780/ref,f823/ref,f860/ref)
    slopes[i],dfs[i] = np.median(slopes_t), np.median(dfs_t)
    # Plot data
    plt.plot(np.array(f780)/np.median(np.array(f780)),cols[i],label = stars[i])
    plt.plot(y[0],cols[i])
    plt.plot(y[1],cols[i])

plt.ylim(0,1.2)
#------------#
# Plot Stuff #
#------------#
plt.figure()
for i in np.arange(len(data)):
    plt.scatter(slopes[i],dfs[i],c=cols[i][0],s=120,label=stars[i])

plt.legend(loc='best')
plt.xlabel('Slope using f780 and f860') 
plt.ylabel('df_823')

plt.figure()
for i in np.arange(len(data)):
    plt.scatter(temps[i],slopes[i],c=cols[i][0],s=120,label=stars[i])

plt.legend(loc='best')
plt.xlabel('Slope using f780 and f860')
plt.ylabel('Temperature from Wiki')


fig, ax = plt.subplots(3,sharex=True)
for i in np.arange(len(data)):
    ax[0].scatter(temps[i],ys[i,0],c=cols[i][0],s=120,label=stars[i]) #823/780
#    ax[0].errorbar(temps[i],ys[i,0],yserr[i,0],ecolor=cols[i][0]) # errors affected by bad pts
    ax[1].scatter(temps[i],ys[i,1],c=cols[i][0],marker='s',s=120) # 860/780
#    ax[1].errorbar(temps[i],ys[i,1],yserr[i,1],ecolor=cols[i][0])
    ax[2].scatter(temps[i],ys[i,1] - ys[i,0],c=cols[i][0],marker='^',s=120,label=stars[i])

fig.subplots_adjust(hspace=0)
ax[2].legend(loc='best')
ax[0].set_ylabel('f823/f780')
ax[1].set_ylabel('f860/f780')
ax[2].set_ylabel('f860/f780 - f823/f780')
ax[2].set_xlabel('Temperature from Wiki')

# ------------------- #
# Forward Model Part: #
# ------------------- #
print 'At the Forward model part'
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

# Trilegal for fake stellar field
V, J, T = lf.trilegal('../inputs/TRILEGAL/fakestarsout_VJ.dat')

# ---------------------- #
# Load Synthetic Spectra #
# ---------------------- #

# Polaris = 6000, 4.3, 0.05
stars = ['polaris','regulus','arcturus','altair']
temps = [6000,12500, 4300, 7000]
loggs = [4.5, 4.0 , 1.5, 4.5]   # must be dvisible by .5
FeHs  = [0.0, 0.0 ,0.0 ,0.0 ]

# Load all spectra for CAMAL stars 
print 'Loading spectra for CAMAL stars'
specs_cam = []
for i,t in enumerate(temps):
    xtemp, ytemp = loadspec(int(np.round(t,-2)), loggs[i], FeHs[i])
    isort = np.argsort(xtemp)
    yspecnew     = tl.interp(xtap,xtemp[isort]/10.0, ytemp[isort])
    specs_cam.append(yspecnew)

airmass = 2.0 # how to i deal with airmass - will make it go up :(
def getfakes(PWV,yspec):
    trans_t = tel_eff * yspec * yray**airmass * np.abs(ytap)**(PWV/cv)
    f1 = 0.33 * .97 * tl.integrate(xtap,filters[0]*0.01* trans_t)
    f2 = 0.26 * tl.integrate(xtap,filters[1]*0.01* trans_t)
    f3 = 0.19 * tl.integrate(xtap,filters[2]*0.01* trans_t)
    return f2/f1, f3/f1

# Get Fake Photometry assuming some PWV for CAMAL data
fakes = np.zeros((len(temps),2))
for i in np.arange(len(temps)):
    fakes[i] = getfakes(15., specs_cam[i])


# Get fake photometry for lots of stellar temperatures
print 'Now Im starting with an array of ~18 temperatures'
T = np.array([3000,3500,4000,4200,4500,4700,5000,5500,6000,6500,7000,8000,9000,10000,
               12000,13000,16000,20000])

morefakes = np.zeros((len(T),2))
for i,t in enumerate(T):
    xtemp, ytemp = loadspec(int(np.round(t,-2)), 4, 0)
    isort = np.argsort(xtemp)
    yspecnew     = tl.interp(xtap,xtemp[isort]/10.0, ytemp[isort])
    morefakes[i] = getfakes(20, yspecnew)
    print i

#camal4n6


#------------#
# Plot Stuff #
#------------#
stars = ['polaris', 'regulus', 'arcturus', 'altair', 'spica']
cols = ['k','b','m','y','c']
plt.figure()
plt.scatter(temps,ys[:,1][2:],c=cols,s=40)
plt.plot(temps,fakes[:,1],'go')
plt.plot(T,morefakes[:,1],'r-')


plt.figure()
plt.scatter(temps,ys[:,0][2:],c=cols,s=40)
plt.plot(temps,fakes[:,0],'go')
plt.plot(T,morefakes[:,0],'r-')
plt.plot(T,morefakes[:,0],'r-')

plt.scatter(temps,ys[:,1][2:]/fakes[:,1],c='k',s=50)



