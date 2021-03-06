# Functions to Calibrate CAMAL Data

import numpy as np
import os
import astropy.io.fits as pyfits

import camal

def makeBias(path2raw,biasfiles):
    """
    Create Median Bias files with biases found in night folder
    
    Note
    ----
    - To use older night's data, copy over the medBIAS.fits file
    - If no medBIAS.fits file found or if no biases in folder found
        then returns 0
    """
    if (np.size(biasfiles) > 0) & (not os.path.isfile(path2raw + "\\medBIAS.fits")):
        bias = []
        for name in biasfiles:
            temp = pyfits.open(name)
            bias.append(temp[0].data)
        medbias = np.median(np.array(bias)[0:40,:,:] ,axis=0)
        hdu=pyfits.PrimaryHDU(medbias)
        hdu.writeto(path2raw + "\\medBIAS.fits")
        print 'Made Median Bias Frame and saved to ' + path2raw + "\\medBIAS.fits"
        del bias #save room     
        return medbias

    elif os.path.isfile(path2raw + "\\medBIAS.fits"):
        medbiasfits = pyfits.open(path2raw + "medBIAS.fits")
        medbias = medbiasfits[0].data
        print 'Loaded Already Made Median Bias Frame'
        return medbias
    else:
        print 'No Biases Found and no pre-made Median Bias Frame Found, \
               returning 0'
        return 0


def makeFlat(path2raw, flatfiles):
    """
    Create the median, normalized Flat fields for each filter
    
    Notes:
    -----
    - If none exists, check if Blue one exists and then load and return all saved flats
      Must copy over these from another night...haven't implemented an automatic copying thing
    - If none exists, return 1
    """
    if (np.size(flatfiles) > 0) & (not os.path.isfile(path2raw + "\\medFLAT_Blue.fits")):
        flats = {}
        flats['Blue'] = []
        flats['Clear'] = []
        flats['Lunar'] =[]
        for name in flatfiles:
            temp = pyfits.open(name)
            tempdat = temp[0].data
            temphdr = temp[0].header
            if temphdr['XBINNING'] == 1:
                mleft,mright = camal.getBinMatrix(size)
                tempdat = camal.rebin(temp[0].data,mleft = mleft,mright=mright)
            flats[temphdr['FILTER']].append((tempdat - medbias)/np.median(tempdat - medbias))
            print 'Added %s to flats for filter %s' %(name,temphdr['FILTER'])
        medflats = {}
        for keys in flats:
            flats[str(keys)] = np.median(flats[str(keys)],axis=0)
            hdu=pyfits.PrimaryHDU(flats[keys])
            hdu.writeto(path2raw + "\\medFLAT_" + keys + ".fits")
            print 'Saved median flat for filter %s' % keys
        return flats
    elif os.path.isfile(path2raw + "\\medFLAT_Blue.fits"):
        flats = {}
        flats['Blue'] = pyfits.open(path2raw + "\\medFLAT_Luminance.fits")[0].data
        flats['Clear'] = pyfits.open(path2raw + "\\medFLAT_Blue.fits")[0].data
        flats['Lunar'] =pyfits.open(path2raw + "\\medFLAT_Filter 5.fits")[0].data
        print 'Loaded Already Made Median Flat Fields'
        return flats
    else:
        flats = 1
        return flats


def makeDark(path2raw, darkfiles):
    """
    Create median dark field for night
    
    Notes:
    -----
    - Right now, don't use darks. Have one for the polaris data.
    
    ToDo:
    ----
    - Implement check on the exposure time
    """
    if (np.size(darkfiles) > 0) & (not os.path.isfile(path2raw + "medDark_2.3.fits")):
        dark = {}
        dark['2.3'] = []
        dark['5.0'] = []
        dark['2.1'] = []
        for name in darkfiles:
            temp = pyfits.open(name)
            exptime = temp[0].header['EXPTIME']
            dark[str(exptime)].append(temp[0].data - medbias)
        darks = {}
        for key in darks:
            darks[key] = np.median(dark[key],axis=0)[0]
            hdu=pyfits.PrimaryHDU(meddark[key])
            hdu.writeto(path2raw + "medDARK_" + key + '.fits')
        return darks
    elif os.path.isfile(path2raw + "medDark_2.3.fits"):
        darks = {}
        darks['2.3'] = pyfits.open(path2raw + "medDARK_2.3.fits")[0].data
        darks['5.0'] = pyfits.open(path2raw + "medDARK_5.0.fits")[0].data
        darks['2.1'] = pyfits.open(path2raw + "medDARK_2.1.fits")[0].data
        print 'Loaded Already Made Median Darks'
        return darks
    else:
        print 'No Dark files found, nor existing file so returning 0'
        darks = 0
        return darks


def badPixels():
    """
    Define bad/hot pixels based on 2x2 binned pixel locations
    - Ashley picked these out pretty much by eye, finding the bad
       ones by looking at plots of convolved slices of the data.
    - Can try using a more reproducible way..
    """
    badpix_x = np.array([234,423,965, 1492, 1525, 1364])
    badpix_y = np.array([881, 1205, 808, 1043, 829, 746])
    return badpix_x, badpix_y


