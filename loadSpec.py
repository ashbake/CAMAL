
# Make this file go copy synthetic spectrum that we want, 
# unzip it, and read the proper wavelength range
# scp abaker@iroquois.physics.upenn.edu:/RAID/cblake/PHOENIX/BT_SETTL/M-0.0/lte094-2.0-0.0.BT-Settl.7.bz2 ~/Downloads/test.bz2

import numpy as np
import os
import sys

def loadspec(Teff, Logg, M_H):
    filename = 'lte%s-%s-%s.BT-Settl.7.bz2' %(format(Teff/100,'03d'), "{:1.1f}".format(Logg), 
                                                "{:1.1f}".format(M_H))
    # Download file need if doesn't exist
    if not os.path.isfile('../inputs/PHOENIX/' + filename.replace('.bz2','')):
        bashcommand = 'scp abaker@iroquois.physics.upenn.edu:/RAID/cblake/PHOENIX/BT_SETTL/M-%s/%s ../inputs/PHOENIX/' %("{:1.1f}".format(M_H),  filename)
        os.system(bashcommand)
        os.system('bunzip2 ../inputs/PHOENIX/%s' %filename)

    # Read File
    f        = open('../inputs/PHOENIX/' + filename.replace('.bz2',''),'rU')
    lines    = f.readlines()
    f.close()
    imin = 10000
    imax = 70000
    lam      = np.zeros(imax-imin)
    logf     = np.zeros(imax-imin)

    # future: Read only til wavelength equals 2000 probs
    for i in np.arange(imax-imin):
        lam[i]  = float(lines[i+imin].split()[0].replace('D', 'E'))
        logf[i] = float(lines[i+imin].split()[1].replace('D', 'E'))

    # Convert Ergs/sec/cm**2/A to photons/sec/cm**2/A
    flux    =  5.03E7 * lam * (10**logf)

    return lam, flux

