# To be copied to night of data and run there
# Extract fluxes from each observation

import numpy as np
import os
from analysis_code import fluxExtract,camal
import matplotlib.pylab as plt
import pyfits

night = '032416'
objname = 'PROCYON'
path2raw = 'C:\\Users\\' + '"Ashley Baker"' + '\\Desktop\\CAMAL\\raw\\' + night + '\\' 
    
# Make list of object filenames if not created yet then load them
# Note how dumb Windows is. how do i rename Ashley Baker dir to camal?
if not os.path.isfile((path2raw + objname + 'list.txt').replace('"','')):
    fluxExtract.fileList(night,objname,path2raw)

datafiles = np.loadtxt(path2raw.replace('"','') + objname + 'list.txt',dtype='str')
darkfiles = np.loadtxt(path2raw.replace('"','') + '/darklist.txt',dtype='str')
biasfiles = np.loadtxt(path2raw.replace('"','') + '/biaslist.txt',dtype='str')
flatfiles =  np.loadtxt(path2raw.replace('"','') + '/flatlist.txt',dtype='str')


# Load Bias Files and median combine
if np.size(biasfiles) > 0:
    bias = []
    for name in biasfiles:
        temp = pyfits.open(path2raw.replace('"','') + name)
        bias.append(temp[0].data)

# take 40 b/c get memory error
medbias = np.median(np.array(bias)[0:40,:,:] ,axis=0)
del bias

# Load dark frames to dictionary by exp time, subtract bias
if np.size(darkfiles) > 0:
    darks = {}
    for name in darkfiles:
        temp = pyfits.open(path2raw.replace('"','') + name)
        exptime = temp[0].header['EXPTIME']
        darks[str(np.int(exptime))] = temp[0].data - medbias

# Load Flats
if np.size(flatfiles) > 0:
    flats = {}
    flats['Luminance'] = []
    flats['Blue'] = []
    flats['Filter 5'] =[]
    for name in flatfiles:
        temp = pyfits.open(path2raw.replace('"','') + name)
        temphdr = temp[0].header
        flats[temphdr['FILTER']].append((temp[0].data - medbias)/np.median(temp[0].data - medbias))


medflats = {}
for keys in flats: 
    flats[str(keys)] = np.median(flats[str(keys)],axis=0)
    
allflux = []
allalt  = []
filt = []
flags = []

bleh = ['0159PROCYON2.fits','0294PROCYON2.fits','0503PROCYON4.fits','0502PROCYON3.fits','0501PROCYON2.fits']

for f in datafiles:
    science, hdr = fluxExtract.loadData(night, f, path2raw)
    print f
    flux, flags_i = fluxExtract.fluxExtract(science,medbias,flats,hdr,plotap=False)
    allflux.append(flux)
    flags.append(flags_i)
    altitude, t = camal.get_altitude(objname,hdr['DATE-OBS'])
    allalt.append(altitude)
    filt.append(hdr['FILTER'])


allflux = np.array(allflux)
allalt = np.array(allalt)
flags = np.array(flags)

# 823
blue = allflux[np.where(np.array(filt) == 'Blue')[0]]
bluealt = allalt[np.where(np.array(filt) == 'Blue')[0]]
bit = np.argsort(bluealt)
noflg_b = np.where(flags[np.where(np.array(filt) == 'Blue')[0]] == 0)

# 860
lum = allflux[np.where(np.array(filt) == 'Luminance')[0]]
lumalt = allalt[np.where(np.array(filt) == 'Luminance')[0]]
lit = np.argsort(lumalt)
noflg_l = np.where(flags[np.where(np.array(filt) == 'Luminance')[0]] == 0)

# 780
five = allflux[np.where(np.array(filt) == 'Filter 5')[0]]
fivealt = allalt[np.where(np.array(filt) == 'Filter 5')[0]]
fit = np.argsort(fivealt)
noflg_f = np.where(flags[np.where(np.array(filt) == 'Filter 5')[0]] == 0)

plt.scatter(np.log(five[fit]/blue[bit]),np.log(lum[lit]/blue[bit]),c=bluealt,s=50)
plt.xlabel(' log( 780/823 )')
plt.ylabel(' log( 860/823 )')
plt.title('color == 823 altitude')

# Plot altitude
plt.plot(1/np.cos((np.pi/180.)*(90 - fivealt[noflg_f])),five[noflg_f]/np.mean(five),'ro',label=('780'))
plt.plot(1/np.cos((np.pi/180.)*(90 - bluealt[noflg_b])),blue[noflg_b]/np.mean(blue[noflg_b])+.2,'bo',label=('823'))
plt.plot(1/np.cos((np.pi/180.)*(90 - lumalt[noflg_l])),lum[noflg_l]/np.mean(lum[noflg_l])+.4,'go',label=('860'))
plt.xlabel('airmass')
plt.ylabel('arbitrary shifted flux')
plt.legend(loc='best')

filtdic = {'Luminance' : 0, 'Blue' : 1, 'Filter 5' : 2}
filtint = []
for i in range(0,len(filt)):
    filtint.append(filtdic[filt[i]])

plt.plot(1/np.cos((np.pi/180.)*(90 - fivealt)),lum/blue,'bo')

DAT = np.array(zip(allflux,allalt,filtint,flags),dtype=[('flux', float),('alt', float), ('filt', int), ('flags', int)])
np.savetxt('FinalData.txt',DAT,fmt='%5f %5f %1i %1i')

