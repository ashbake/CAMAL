# Class to loadfiles
# Read to objects.py??

import matplotlib.pylab as plt
import numpy as np
import pyfits
from astropy.time import Time
from scipy import ndimage
plt.ion()


class loadfile():
    def __init__(self):
        print 'camal, suominet, tapas, rayleigh, filters, trilegal, phoenix'

    def camal(self,filename):
        """
        Load CAMAL night's data file post reduction
        -Read file
        -save data points that are in a trio
        -reject data points that are nonsensical

        Return
        ------
        arrays: f780, f823, f860, time [# good observation cycles]

        Notes
        -----
        Only save one time for three filters...can change that
        Can also change to return more things
        """
        # Read Filename
        hdulist = pyfits.open(filename)
        data = hdulist[1].data

        # Load file's parameters
        allflux = data['allflux']
        allalt = data['allalt']
        filter = data['filter']
        expTime = data['expTime']
        xcent = data['Xcenter']
        ycent = data['Ycenter']
        JD = data['JD']

        # Initiate arrays to match each filter
        i=0
        f780 = []
        f823 = []
        f860 = []
        alt = []
        time = []
        while i < (len(allflux)-2):
            # Filter out bad ones and nonconsecutive trios
            if (24*3600*(JD[i + 2] - JD[i]) < ( 13.0 + sum(expTime[i:i+3]))) \
                    & (len(set(filter[i:i+3])) == 3) & (filter[i]=='Blue') & all(allflux[i:i+3] > 0):
                f823.append(allflux[i])
                f860.append(allflux[i+1])
                f780.append(allflux[i+2])
                time.append(JD[i])
                alt.append(allalt[i])
                i += 3
            else:
                print 'skipping data line %r' %i
                i += 1

        # Return fluxes, time
        return f780, f823, f860, time
    
    def suominet(self,filename):
        """
        Load PWV data from GPS monitoring system
        -Convert time to JD
        
        Return:
        -------
        arrays: time, PWV, PWVerr [len(PWV file)]
        """
        # Read data file using genfromtxt
        dat = np.genfromtxt(filename, dtype=None,
              names=('loc', 'date', 'PWV', 'PWVerr', 'null1', 'TZD',
                     'null2','press', 'temp', 'hum', 'null3', 'null4', 'null5', 'null6'))

        # Convert times to julian date
        times = Time(dat['date']).jd

        # Return useful things
        return times, dat['PWV'], dat['PWVerr']

    def tapas(self,filename):
        """
        Load Tapas atmospheric spectrum sans rayleigh
        """
        tapas = np.loadtxt(filename)
        lam = tapas[:,0]
        trans = tapas[:,1]
        return lam, trans
        
    def rayleigh(self,filename):
        """
        Load Rayleigh scattering spectrum
        """
        f = open(filename)
        lines = f.readlines()
        f.close()
        
        lam   = []
        trans = []

        for i, line in enumerate(lines):
            if not lines[i][0].startswith('#'):
                lam[i]   =  float(lines[i].split()[0])
                trans[i] =  float(lines[i].split()[1])
        return np.array(lam), np.array(trans)

    def filters(self,filenames,lam):
        """
        Load filter profiles and interpolate on lam given
        
        Return:
        ------
        filty:  list [len(filenames)]
          filter y value (0 to 1) interpolated at lam
        """
        filty = []
        for f in filenames:
            filt = np.loadtxt(f)
            int_filt  = interp1d(filt[:,0],filt[:,1],fill_value = 0,
                           bounds_error=False)
            filty.append(int_filt(lam))
        
        # Return filters
        return filty
    
    def trilegal(self,filename):
        """
        Load J,H,K from trilegal field
        """
        f = open(filename)
        lines = f.readlines()
        f.close()

        # Expect only one header
        for j, lab in enumerate(lines[0].split()):
            if lab.startswith('logTe'):
                iT = j
            if lab.startswith('V'):
                iV = j
            if lab.startswith('J'):
                iJ = j

        V   = []
        J   = []
        T   = []

        for i in np.arange(len(lines)-2):
            V.append(float(lines[i+1].split()[iV]))
            J.append(float(lines[i+1].split()[iJ]))
            T.append(float(lines[i+1].split()[iT]))

        return np.array(V), np.array(J), 10**np.array(T)

    def phoenix(self,filename,wave0,wave1,convolve = False):
        """Load synthetic spectra                                          
        wave0, wave1: in angstroms                                     
        Polaris:                                                                     
        filename = te06000-2.00+0.5.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits"""
        # Load data
        wave = 0.1 * pyfits.open('../inputs/WAVE_PHOENIX-ACES-AGSS-COND-2011.fits')[0].data
        flux = pyfits.open(filename)[0].data

        # Cut out wavelengths
        wlo = np.where(np.diff((wave > wave0).astype(int)) == 1)[0][0]
        whi = np.where(np.diff((wave > wave1).astype(int)) == 1)[0][0]

        if convolve:
            fluxout = ndimage.filters.gaussian_filter(flux[wlo:whi], 100, mode='nearest')
            return wave[wlo:whi], fluxout
        else:
            return wave[wlo:whi], flux[wlo:whi]





from scipy.interpolate import interp1d
from scipy.integrate import trapz

class tools():
    """
    
    """
    def __init__(self):
        print 'tools for camal'
    
    def bindat(self,x,y,nbins):
        """
        Bin Data
        
        Inputs:
        ------
        x, y, nbins
        
        Returns:
        --------
        arrays: bins, mean, std  [nbins]
        """
        # Create bins (nbins + 1)?
        n, bins = np.histogram(x, bins=nbins)
        sy, _ = np.histogram(x, bins=nbins, weights=y)
        sy2, _ = np.histogram(x, bins=nbins, weights=y*y)
        
        # Calculate bin centers, mean, and std in each bin
        bins = (bins[1:] + bins[:-1])/2
        mean = sy / n
        std = np.sqrt(sy2/n - mean*mean)
        
        # Return bin x, bin y, bin std
        return bins, mean, std

    def integrate(self,x,y):
        """
        Integrate y wrt x
        """
        return trapz(y,x=x)
    
    def alt_to_amass(self,altitude):
        """
        Convert altitude (degrees) to airmass
        """
        return 1/np.cos(1-altitude*np.pi/180.0)

    def getpt(self,y780,y860):
        """
        Calculate point at 823nm if draw a line through
        the fluxes at 780nm and 860nm
        """
        slope = (y780-y860)/(780.-860.)
        return slope *(823.-780)+ y780

    def interp(self,xnew, xold, yold):
        """
        interpolate xold and yold, return ynew
        """
        interfxn  = interp1d(xold, yold, fill_value = 0, bounds_error=False)
        yphoe     = interfxn(xnew)
        return yphoe
