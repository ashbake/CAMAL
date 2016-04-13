import time
import win32com.client
import logging
import cTelescope

night = time.strftime("%m%d%y")
# Start Log File
logger = cTelescope.cLog( night + '.log')

# Connect via win32 
tele = win32com.client.Dispatch("ACP.Telescope")
SUP = win32com.client.Dispatch("ACP.AcquireSupport")
CHOOSER = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
CHOOSER.DeviceType = 'Telescope'
APPL = win32com.client.Dispatch("MaxIm.Application")

if not tele.Connected:
    tele.Connected = True

# Set up tele properties. Do these once, including setting limits so
# camera doesn't hit. print these to log for night
logger.info('Focal Length = ' + str(tele.FocalLength))
logger.info('Aperture Diameter = ' + str(tele.ApertureDiameter))     

if tele.CanUnpark:
    tele.Unpark

tele.SiteLatitude = 39.952108
tele.SiteLongitude = -75.188953

RA = 5
DEC = 20  
if tele.CanSync:
    tele.SlewToCoordinatesAsync(RA,DEC)
    while tele.Slewing:
        time.sleep(1)

# how to set limits on max and min altitude so camera doesnt hit
# 
tele.TrackingRate = 0 # 0 == Sidereal
DECrate = 10 #arcseconds per second
RArate = 10 #arcseconds per second
tele.DeclinationRate = DECrate
tele.RightAscensionRate = RArate

targetDEC = 20.   # degrees , + 
targetRA = 5.     # degrees

tele.TargetDeclination = targetDEC
tele.TargetRightAscension = targetRA

tele.PulseGuide(0,1000) # north DEC + 1sec
tele.PulseGuide(2,1000) # east RA, +, 1000ms
while tele.IsPulseGuiding:
    time.sleep(1)
#how to set slew rates?


