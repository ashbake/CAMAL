#!/usr/bin/python

#Camal module
import numpy as np
from scipy import signal
import scipy
from photutils import CircularAnnulus
import photutils
from photutils import aperture_photometry, CircularAperture
import pyfits
import pylab
import matplotlib.pylab as plt
from astropy.time import Time
import cPickle as pickle
#starlist = pickle.load( open( "starlist.p", "rb" ) )

starlist = {}
starlist['test'] = [114.825498,5.224988]
starlist['PROCYON'] = [114.825498,5.224988]

__all__ = ['gaussian','tophat','fxnmean','fxnvariance','plot_apertures', 'get_altitude']

def gaussian(x, shift, sig):
    ' Return normalized gaussian with mean shift and var = sig^2 '
    return np.exp(-.5*((x - shift)/sig)**2)/(sig * np.sqrt(2*np.pi))


def tophat(x, shift, sig):
    fxn = np.zeros(len(x))
    middle = np.int(shift)
    fxn[middle - sig/2:middle + sig/2] = 1
    return fxn


def fxnmean(x,y):
    ' Integrate x times y over interval a to b to get PDF mean value '
    return scipy.integrate.simps(x * np.array(y)/sum(y), x, dx = x[3]-x[2])


def fxnvariance(x,y,mean):
    ' Integrate (x-mean)^2 *f(x) over interval a to b to get PDF var '
    return scipy.integrate.simps((x - mean)**2 * y/sum(y),x,dx=x[3]-x[2])
    
    
def plot_apertures(image, positions, radius):
    apertures = CircularAperture(positions, r=radius)
    phot_table = aperture_photometry(image, apertures)
    plt.imshow(image, cmap='gray_r', origin='lower')
    apertures.plot(color='red', lw=3.5, alpha=0.5)


def get_altitude(starname, timestr):
    #look up starname in dictionary and provide timestr - time of observ in header
    RA =  starlist[starname][0] #deg
    DEC = np.abs(starlist[starname][1]) #deg
    #Philadelphia LAT LONG (change when go to MT Hopkins)
    LAT  = 39.95 #deg
    LONG = -75.15 #deg
    # date time must be UT (greenwich), everything in degrees, (long, lat)
    ###timestr = '2015-12-06T00.04.10.000'
    t=Time(timestr.replace(".", ":", 2), format='isot', 
           location=(np.str(LONG)+'d',np.str(LAT) + 'd'))
    t.delta_ut1_utc = 0.0
    LST = t.sidereal_time('apparent').deg # or .rad or .hour
    LHA = LST - RA
    #Make LHA be between 0 and 360
    while LHA < 0:
        LHA = LHA + 360.
    while LHA > 360:
        LHA = LHA - 360.
    # calculate altitude 
    altitude = np.arcsin(np.sin(LAT*np.pi/180.) * np.sin(DEC*np.pi/180.)  + np.cos(LAT*np.pi/180.) * np.cos(DEC*np.pi/180.) * np.cos(LHA*np.pi/180.))*180/np.pi
    if altitude < 0:
        altitude = altitude + 90.
    return altitude,t





