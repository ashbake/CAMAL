#!/usr/bin/python

#Camal module
import numpy as np
from scipy import signal
import scipy
from photutils import CircularAnnulus
import photutils
from photutils import aperture_photometry, CircularAperture
import astropy.io.fits as pyfits
import pylab
import matplotlib.pylab as plt
from astropy.time import Time
import cPickle as pickle
#starlist = pickle.load( open( "starlist.p", "rb" ) )

starlist = {}
starlist['test'] = [114.825498,5.224988]
starlist['PROCYON'] = [114.825498,5.224988]
starlist['castor'] = [113.649472,31.888282]
starlist['polaris'] = [37.954561, 89.264109]
starlist['vega'] = [279.23,38.7] 
starlist['altair'] = [297.7,8.87]
starlist['arcturus'] = [213.9, 19.18]
starlist['spica'] = [201.3,-11.16]
starlist['regulus'] = [152.1,11.97]
starlist['Rigel'] = [78.6,-8.2]

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


def get_altitude(RA,DEC, timestr):
    LAT  = 31.6 # philly 39.95 #deg
    LONG = -110.9 #-75.15 #deg
    # date time must be UT (greenwich), everything in degrees, (long, lat)
    ###timestr = '2015-12-06T00.04.10.000'
    #t=Time(timestr.replace(".", ":", 2), format='isot', 
    #       location=(np.str(LONG)+'d',np.str(LAT) + 'd'))
    t=Time(timestr, format='jd', 
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


def rebin1to2(ccdim,mleft=None,mright=None):
    'rebins ccd image as np.array from 1x1 to 2x2'
    'using matrix multiplication'
    'if no mLeft given, will make them'
    size = np.shape(ccdim)
    if mleft==None:
        mleft = np.zeros((size[0]/2,size[0]))
        mright = np.zeros((size[1],size[1]/2))
        for i in range(0,size[0]/2):
            mleft[i,2*i] = 1
            mleft[i,2*i+1] = 1
        for i in range(0,size[1]/2):
            mright[2*i,i] = 1
            mright[2*i+1,i] = 1
    tempout = np.dot(ccdim,mright)
    return np.dot(mleft, tempout)
    
def getBinMatrix(size):
    'input size of matrix'
    mleft = np.zeros((size[0]/2,size[0]))
    mright = np.zeros((size[1],size[1]/2))
    for i in range(0,size[0]/2):
        mleft[i,2*i] = 1
        mleft[i,2*i+1] = 1
    for i in range(0,size[1]/2):
        mright[2*i,i] = 1
        mright[2*i+1,i] = 1
    return mleft,mright



def cleanData(path2raw,night,object):
    ' Remove bad points '
    data = pyfits.open('%sfinalData_%s_%s.fits' %(path2raw,night,object))[1].data

    # Load Variables/data
    # -------------------                                                      
    allflux = data['allflux']
    allalt = data['allalt']
    filter = data['filter']
    expTime = data['expTime']
    xcent = data['Xcenter']
    ycent = data['Ycenter']
    JD = data['JD']

    # Divide into filters excluding nonconsecutive ones
    # -------------------------------------------------                 
    i=0
    f780 = []
    f823 = []
    f860 = []
    alt = []
    time = []
    while i < (len(allflux)-2):
        if (24*3600*(JD[i + 2] - JD[i]) < ( 13.0 + sum(expTime[i:i+3]))) & (len(set(filter[i:i+3])) == 3) \
                & (filter[i]=='Blue') & all(allflux[i:i+3] > 0):
            f823.append(allflux[i])
            f860.append(allflux[i+1])
            f780.append(allflux[i+2])
            time.append(JD[i])
            alt.append(allalt[i])
            i += 3
        else:
            print i
            i += 1
    ref = np.median(f780)
    f780 = np.array(f780)/ref
    f823 = np.array(f823)/ref
    f860 = np.array(f860)/ref
    
    return time, f780, f823, f860

def bindat(x,y,nbins):
    n, bins = np.histogram(x, bins=nbins)
    sy, _ = np.histogram(x, bins=nbins, weights=y)
    sy2, _ = np.histogram(x, bins=nbins, weights=y*y)
    bins = (bins[1:] + bins[:-1])/2
    mean = sy / n
    std = np.sqrt(sy2/n - mean*mean)
    return bins,mean,std
