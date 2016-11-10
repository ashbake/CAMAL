# To be copied to night of data and run there
# Extract fluxes from each observation
# images must be full (no subframe)
# if binning 1x1 by mistake, this is fixed with rebin1to2

import numpy as np
import os
import matplotlib.pylab as plt
import astropy.io.fits as pyfits
import glob 
from astropy.time import Time 

from cAnalysis import fluxExtract,camal,calibrate

# Night, Object Inputs
# -------------------
night = '10 28 2016'
objname = 'Rigel'
# -------------------

# Define path where all the data are
dataPath =  'C:\Users\Ashley Baker\Documents\Software Bisque\TheSkyX Professional Edition\Camera AutoSave\Imager'
path2raw = dataPath + '\\' + night 

# Load bad pixels in 2x2 binning
badpix_x, badpix_y = calibrate.badPixels()


# Load Lists of filenames for Data & Calibration, 
# Can edit these txt files directly to exclude a file
datafiles = glob.glob(path2raw +  '\\*' + objname + '.fit')
darkfiles = glob.glob(path2raw + '\\*DARK.fits')
biasfiles = glob.glob(path2raw + '\\*BIAS.fits')
flatfiles = glob.glob(path2raw + '\\*FLAT.fits')

# Make or Load Calibration Files, Save in Raw folder
bias = calibrate.makeBias(path2raw, biasfiles)
flat = calibrate.makeFlat(path2raw, flatfiles)
dark = calibrate.makeDark(path2raw, darkfiles)


# Matrices for redoing the binning if going from binning of 1 to binning of 2
mleft,mright = camal.getBinMatrix((2532, 3352))


# Flux extract --- put this fluxExtract.py eventually
# also use f = open('fluxfilename.txt','w')
allflux = []
allalt  = []
filt = []
flags = []
exptime = []
centx = []
centy = []
bkg_means = []
juldate = []

skip = 0
skipto = len(allflux)+1
for f in datafiles:
    if skip < skipto:
        skip+=1
    else:
        print f
        science, hdr = fluxExtract.loadData(f)
        if hdr['XBINNING'] == 1:
            science = camal.rebin1to2(science,mleft = mleft,mright=mright)
        science[badpix_y,badpix_x] = science[badpix_y+1,badpix_x+1]
        flux, flags_i,x,y,bkg_mean = fluxExtract.fluxExtract(science,bias,dark,flat,hdr,plotap=False)
        # Save Things
        allflux.append(flux)
        flags.append(flags_i)
        altitude, t = camal.get_altitude(objname,hdr['DATE-OBS'])
        allalt.append(altitude)
        filt.append(hdr['FILTER'])
        exptime.append(hdr['EXPTIME'])
        centx.append(x)
        centy.append(y)
        bkg_means.append(bkg_mean)
        juldate.append(Time(hdr['DATE-OBS']).jd)
        #juldate.append(hdr['JD'])

allflux_raw = np.array(allflux)
allflux = np.array(allflux_raw)/np.array(exptime)
allalt = np.array(allalt)
flags = np.array(flags)

#filtdic = {'Luminance' : 0, 'Blue' : 1, 'Filter 5' : 2}
filtdic  = {'Blue' : 823, 'Clear' : 860, 'Lunar' : 780}
filtint = []
for i in range(0,len(filt)):
    filtint.append(filtdic[filt[i]])


# Save to Fits
tbhdu = pyfits.BinTableHDU.from_columns(
     [pyfits.Column(name='allflux', format='E', array=np.array(allflux)),
      pyfits.Column(name='allalt', format='E', array=np.array(allalt)),
      pyfits.Column(name='filter', format='20A',array=np.array(filt)),
      pyfits.Column(name='expTime',format='E',array=np.array(exptime)),
      pyfits.Column(name='Xcenter',format='E',array=np.array(centx)),
      pyfits.Column(name='Ycenter',format='E',array=np.array(centy)),
      pyfits.Column(name='BkgMeanCount',format='E',array=np.array(bkg_means)),
      pyfits.Column(name='JD',format='D',array=np.array(juldate)) ])

tbhdu.writeto(path2raw + 'finalData_' + night + '_' + objname + '.fits')






# ------------------ 
