# Script to take sky flats
# Run as execfile('../../../Scripts/takeFlats.py')
import time
import win32com.client
import pyfits
import numpy as np

night = '032116\\' #(MMDDYY) make new folder
path  = 'C:\Users\Ashley Baker\Desktop\CAMAL\raw' + '\\' + night
object = 'calibration'    # star ID number or name in star dictionary



try:
    tag            # Don't wanna rename files the same thing
except NameError:
    tag = 0        # Image number taken from beginning of night
else:
    print 'tag = ', tag


CAMERA = win32com.client.Dispatch("MaxIm.CCDCamera")
DOC = win32com.client.Dispatch("MaxIm.Document")
CAMERA.DisableAutoShutdown = True
CAMERA.LinkEnabled = True
CAMERA.AutoDownload = True

ambTemp = CAMERA.AmbientTemperature
if not CAMERA.CoolerOn:
    CAMERA.CoolerOn = True
    CAMERA.TemperatureSetpoint = ambTemp - 20.0
    #while CAMERA.CoolerPower < 50:
        #time.sleep(1)
else:
    print "WARNING: Cooler already on. Did not cool more."

CAMERA.BinX = 2
CAMERA.BinY = 2
                
length = 3 #sec
outarr={}
# Cycle through filters before saving


for filterSlot in range(3,5):
    CAMERA.Expose(length,1,filterSlot)
    while not CAMERA.ImageReady:
        time.sleep(1)
    outarr[str(filterSlot)] = DOC.ImageArray
    
# Save 
for filterSlot in range(3,5):
    hdu = pyfits.PrimaryHDU(outarr[str(filterSlot)])
    hdu.writeto(format(tag,"04") + object + '.fits')
    tag += 1
    
maxPixel, minPixel, average, stddev = image.CalcAreaInfo(0, 0, image.XSize-1, image.YSize-1)
            print "Average: %.2f, StdDev: %.2f" % (average, stddev)
            
plt.imshow(outarr['4'])
    
    