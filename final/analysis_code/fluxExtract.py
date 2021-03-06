# CAMAL Reduction Class for CAMAL data
# 

import os
import matplotlib.pylab as plt
from photutils import datasets
from sigma_clipping import sigma_clip,sigma_clipped_stats
#from astropy.stats import sigma_clipped_stats #not sure why wont work
import numpy as np
from photutils import daofind, CircularAperture,CircularAnnulus,aperture_photometry
import astropy.io.fits as pyfits
import scipy
from scipy import signal
import camal
plt.ion()

__all__ = ['fileList','loadData','fluxExtract','sourceFinder'] 


def fileList(night,objname,path2raw):
    ' Creates lists for each image type: science, dark, flat, bias '
    # Maybe in the future should just store calibration imgs in one folder so 
    # don't have to take them every night. Then can just choose the most recent
    os.system('ls ' + path2raw + '*' + objname + '*fits  | xargs -n 1 basename  > ' + path2raw + objname + 'list.txt')
    os.system('ls ' + path2raw + '*DARK*fit*  | xargs -n 1 basename > ' + path2raw + 'darklist.txt')
    os.system('ls ' + path2raw + '*FLAT*fit*  | xargs -n 1 basename > ' + path2raw + 'flatlist.txt')
    os.system('ls ' + path2raw + '*BIAS*fit*  | xargs -n 1 basename > ' + path2raw + 'biaslist.txt')
    print 'Creating File Lists in' + path2raw
    

def loadData(filename):
    ' Load data and return data array and header '
    dat = pyfits.open(filename)
    return dat[0].data, dat[0].header


def sourceFinder(science):
    ' Input: loaded data, Output: x,y center of aperture '
    # Convolve image with gaussian kernel
    kernel = np.outer(signal.gaussian(50,8), signal.gaussian(50,8))
    blurred = signal.fftconvolve(science, kernel, mode='same')
   
    # Take the normalized STD along x,y axes
    xstd = np.std(blurred,axis=0)
    ystd = np.std(blurred,axis=1)
    xstdn = (xstd - np.median(xstd[200:300]))/max(xstd)
    ystdn = (ystd - np.median(ystd[200:300]))/max(ystd)
    
    # Determine center by maximum. Eventually add check that there's only one source!
    try: x,y = np.where(xstdn == max(xstdn))[0][0], np.where(ystdn == max(ystdn))[0][0]
    except IndexError:
        x,y = 0,0
        
    return x,y



def fluxExtract(science,bias,dark,flats,hdr,plotap=False,rad=17):
    ' Returns final flux of source '
    # Calibrate Image. Flatten? add bias and flat to input
    flagg = 0
    
    if flats == 0:
        flat = np.ones(np.shape(science))
    else:
        flat = flats[hdr['FILTER']]
    
    if dark == 0:
        dark = np.ones(np.shape(science))
    else:
        dark = dark[str(hdr['EXPTIME'])]

    if np.mean(bias) == 0:
        bias = np.zeros(np.shape(science))
    else:
        bias = bias

    data = (science - bias - dark)/flat
    
    if np.mean(data) < 0:
        flagg += 1
        
    # Get source x,y position
    x,y = sourceFinder(science)
    positions = (x,y)
    
    if x==0:
        flagg += 1
    
    if y==0:
        flagg += 1
        
    # Define Apertures
    apertures = CircularAperture(positions, r=rad)
    annulus_apertures = CircularAnnulus(positions, r_in=22., r_out=33.)

    # Get fluxes
    rawflux_table = aperture_photometry(data, apertures)
    bkgflux_table = aperture_photometry(data, annulus_apertures)
    phot_table = np.hstack([rawflux_table, bkgflux_table])
    bkg_mean = phot_table['aperture_sum'][1] / annulus_apertures.area()
    bkg_sum = bkg_mean * apertures.area()
    final_sum = phot_table['aperture_sum'][0] - bkg_sum

    # Plot
    if plotap == True:
        plt.imshow(np.log(data), origin='lower')
        apertures.plot(color='red', lw=1.5, alpha=0.5)
        annulus_apertures.plot(color='orange', lw=1.5, alpha=0.5)

    return final_sum,flagg,x,y,bkg_mean

