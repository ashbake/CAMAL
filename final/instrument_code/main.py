

import camal_class_files.mysite as camalsite
import camal_class_files.cCamera as camalimager
import camal_class_files.cTelescope as camaltelescope
import camal_class_files.mail as mail
import numpy as np
from camal_class_files.get_centroid import *
import shutil, re

import datetime, logging, os, sys, time, subprocess, glob, math, json, copy
import ipdb
import socket, threading, ephem
import astropy.io.fits as pyfits
from scipy import stats

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive



def endNight(site, telescope, imager):

    # park the scope
    try: logger.info("Parking/Disconnection from Telescope")
    except: pass
    telescope.shutDown()
    
    # Backup the data
    try: logger.info("Compressing data")
    except: pass
    compressData(imager.dataPath) # does nothing

    # Turn off the camera cooler, disconnect
    try: logger.info("Disconnecting imager")
    except: pass
    try: imager.shutDown()
    except: pass

    #TODO: Back up the data
    try: logger.info("Backing Up data")
    except: pass
    backupData(imager.dataPath) # does nothing


    # copy schedule to data directory
    try: logger.info("Copying schedule file from ./schedule/" + site.night + ".txt to " + imager.dataPath)
    except: pass
    shutil.copyfile("./schedule/" + site.night + ".txt", imager.dataPath + site.night + ".txt")

    # copy logs to data directory
    logs = glob.glob("./logs/" + site.night + "/*.log")
    for log in logs:
        try: logger.info("Copying log file " + log + " to " + imager.dataPath)
        except: pass
        shutil.copyfile(log, imager.dataPath + os.path.basename(log))

    #### create an observing report ####

    # compose the observing report
    body = "Dear humans,\n\n" + \
           "While you were sleeping, I observed:\n\n"

    body += "\nPlease check the data on ashley's google drive. \n"
           "Love,\n" + \
            "CAMAL"

    # email observing report
    mail.send('camal is done observing',body)


def prepNight(email=True):

    # reset the night at 10 am local
    today = datetime.datetime.utcnow()
    if datetime.datetime.now().hour >= 10 and datetime.datetime.now().hour <= 16:
        today = today + datetime.timedelta(days=1)
    night = 'n' + today.strftime('%Y%m%d')

    # make sure the log path exists
    logpath = 'logs/' + night + '/'
    if not os.path.exists(logpath):
        os.makedirs(logpath)
        
    hostname = socket.gethostname()

    site = camalsite.site('Mount_Hopkins',night,configfile='camal_class_files/site.ini')
    site.night = night

    site.startNightTime = datetime.datetime(today.year, today.month, today.day, 17) - datetime.timedelta(days=1)

    telescope = camaltelescope.cMyT()
    imager = camalimager.cSBIG()

    imager.dataPath = "C:/camal/data/" + night + "/"

    if not os.path.exists(imager.dataPath):
        os.makedirs(imager.dataPath)

    # email notice
    if email: mail.send('CAMAL Starting observing','Love,\nCAMAL')

    return site, telescope, imager


def compressData(dataPath):
    files = glob.glob(dataPath + "/*.fit")
    for filename in files:
        logger.info('Compressing ' + filename)
        subprocess.call(['cfitsio/fpack.exe','-D',filename])

def backupData(dataPath):
    files = glob.glob(dataPath + "/*.fit")
    #gauth = GoogleAuth()
    #gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    #drive = GoogleDrive(gauth)



def doBias(site, telescope, imager, num=11):
    doDark(site, telescope, imager,exptime=0,num=num)

def doDark(site, aqawan, telescope, imager, exptime, num):
    DARK = 0
    if exptime == 0:
        objectName = 'Bias'
        for x in range(num):    
            logger.info('Taking ' + objectName + ' ' + str(x+1) + ' of ' + str(num) + ' (exptime = ' + str(exptime) + ')')
            takeImage(site, aqawan, telescope, imager, exptime,'V',objectName)
    else:
        objectName = 'Dark'
        # Take num Dark frames and loop over more than one exptime
        for time in exptime:
            for x in range(num):    
                logger.info('Taking ' + objectName + ' ' + str(x+1) + ' of ' + str(num) + ' (exptime = ' + str(time) + ')')
                takeImage(site, aqawan, telescope, imager, time,'V',objectName)

def getMean(filename):
    image = pyfits.getdata(filename,0)
    return image.mean()

def getMode(filename):
    image = pyfits.getdata(filename,0)

    # mode is slow; take the central 100x100 region
    # (or the size of the image, which ever is smaller)
    nx = len(image)
    ny = len(image[1])
    size = 100
    x1 = max(nx/2.0 - size/2.0,0)
    x2 = min(nx/2.0 + size/2.0,nx-1)
    y1 = max(ny/2.0 - size/2.0,0)
    y2 = min(ny/2.0 + size/2.0,ny-1)
    
    return stats.mode(image[x1:x2,y1:y2],axis=None)[0][0]

def isSupersaturated(filename):
    image = pyfits.getdata(filename,0)

    # mode is slow; take the central 100x100 region
    # (or the size of the image, which ever is smaller)
    nx = len(image)
    ny = len(image[1])
    size = 100
    x1 = max(nx/2.0 - size/2.0,0)
    x2 = min(nx/2.0 + size/2.0,nx-1)
    y1 = max(ny/2.0 - size/2.0,0)
    y2 = min(ny/2.0 + size/2.0,ny-1)

    photonNoise = 10.0 # made up, should do this better
    if np.std(image[x1:x2,y1:y2],axis=None) < photonNoise:
        return True
    
    return False


def takeImage(site, telescope, imager, exptime, filterInd, objname):

    exptypes = {
        'Dark' : 0,
        'Bias' : 0,
        'SkyFlat' : 1,
        }

    if objname in exptypes.keys():
        exptype = exptypes[objname]
    else: exptype = 1 # science exposure

    if filterInd not in imager.filters:
        logger.error("Requested filter (" + filterInd + ") not present")
        return
   
    # Take image
    logger.info("Taking " + str(exptime) + " second image")
    t0 = datetime.datetime.utcnow()
    imager.cam.Expose(exptime, exptype, imager.filters[filterInd])

    # Get status info for headers while exposing/reading out 
    telra = ten(telescope.getRA)*15.0
    teldec = ten(telescope.getDEC)
    ra = ten(telescopeStatus.mount.ra_target)*15.0
    dec = ten(telescopeStatus.mount.dec_target)
    if dec > 90.0: dec = dec-360 # fixes bug in PWI

    moonpos   = site.moonpos()
    moonra    = moonpos[0]
    moondec   = moonpos[1]
    moonsep   = ephem.separation((telra*math.pi/180.0,teldec*math.pi/180.0),moonpos)*180.0/math.pi
    moonphase = site.moonphase()

    try:
        while not imager.cam.ImageReady:
            if (datetime.datetime.utcnow()-t0).total_seconds() > (exptime  + 60):
                logger.error("Imager has been reading out for over a minute; beginning recovery")
                imager.nfailed=max([1,imager.nfailed])
                imager.recover()
                imager.connect()
                # try again
                return takeImage(site, aqawan, telescope, imager, exptime, filterInd, objname)
            time.sleep(0.01)
    except:
        logger.error("Camera failure: " + str(sys.exc_info()[0]))
        mail.send("Camera failure on " + telescope.name,"Camera failure on " + telescope.name + ": " + str(sys.exc_info()[0]) + "\n\nPlease reconnect, power cycle the panel, or reboot the machine.\n\nLove,\n" + telescope.name, level='serious')
        imager.nfailed=1
        imager.recover()
        imager.connect()

    # Save the image
    filename = imager.dataPath + "/" + site.night + "." + telescope.name + "." + objname + "." + filterInd + "." + getIndex(imager.dataPath) + ".fits"
    logger.info('Saving image: ' + filename)
    imager.cam.SaveImage(filename)

    # This only takes 15 ms
    logger.debug('Opening ' + filename + " to modify header")


