import time
import win32com.client
 
ERROR = True
NOERROR = False
 
##------------------------------------------------------------------------------
## Class: cCamera
##------------------------------------------------------------------------------
class cCamera:
    def __init__(self):
        print "Connecting to MaxIm DL..."
        self.__CAMERA = win32com.client.Dispatch("MaxIm.CCDCamera")
        self.__CAMERA.DisableAutoShutdown = True
        try:
            self.__CAMERA.LinkEnabled = True
        except:
            print "... cannot connect to camera"
            print "--> Is camera hardware attached?"
            print "--> Is some other application already using camera hardware?"
            raise EnvironmentError, 'Halting program'
        if not self.__CAMERA.LinkEnabled:
            print "... camera link DID NOT TURN ON; CANNOT CONTINUE"
            raise EnvironmentError, 'Halting program'
 
    def exposeLight(self,length,filterSlot):
        print "Exposing light frame..."
        self.__CAMERA.Expose(length,1,filterSlot)
        while not self.__CAMERA.ImageReady:
            time.sleep(1)
        print "Light frame exposure and download complete!"
 
    def exposeDark(self,length,filterSlot):
        print "Exposing Dark frame..."
        self.__CAMERA.Expose(length,0,filterSlot)
        while not self.__CAMERA.ImageReady:
            time.sleep(1)
        print "Dark frame exposure and download complete!"
        
        
    def setFrame(self,opt,x,y,wx,wy):
        if opt == 'full':
            self.__CAMERA.SetFullFrame()
            print "Camera set to full-frame mode"
        if opt == 'sub':
            self.__CAMERA.StartX = x
            self.__CAMERA.StartY = y
            self.__CAMERA.NumX = wx
            self.__CAMERA.NumY = wy
            print "Camera set to subframe. Note: Inputs must consider binning."
        else:
            print "Set opt to either 'full' or 'sub'"
        

    def setBinning(self,binmode):
        tup = (1,2,3)
        if binmode in tup:
            self.__CAMERA.BinX = binmode
            self.__CAMERA.BinY = binmode
            print "Camera binning set to %dx%d" % (binmode,binmode)
            return NOERROR
        else:
            print "ERROR: Invalid binning specified"
            return ERROR


    def saveImage(self,filename):
        try:
            self.__CAMERA.SaveImage(filename)
            print "saved file to ", filename
        except:
            print "Cannot save file"
            raise EnvironmentError, 'Halting program'


 
    def coolCCD(self,dt):
        ambTemp = self.__CAMERA.AmbientTemperature
        if not self.__CAMERA.CanSetTemperature:
            print "ERROR: cannot change temperature"
        elif self.__CAMERA.CoolerOn:
            print "ERROR: Cooler already on."
        else:
            self.__CAMERA.CoolerOn = True
            self.__CAMERA.TemperatureSetpoint = ambTemp - dt
            print "Cooling camera to ", str(dt), " C below " , str(ambTemp)
            print "Waiting for Cooler Power to Stabalize Below 50%"
            while self.__CAMERA.CoolerPower < 50:
                time.sleep(1)
            

##
##    END OF 'cCamera' Class
##
