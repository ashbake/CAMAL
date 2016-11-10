import time
import win32com.client
 
ERROR = True
NOERROR = False
 
##------------------------------------------------------------------------------
## Class: cCamera
##------------------------------------------------------------------------------

class cSBIG:
    def __init__(self):
        print "Connecting to MaxIm DL..."
        self.CAMERA = win32com.client.Dispatch("MaxIm.CCDCamera")
        self.CAMERA.DisableAutoShutdown = True
        try:
            self.CAMERA.LinkEnabled = True
        except:
            print "... cannot connect to camera"
            print "--> Is camera hardware attached?"
            print "--> Is some other application already using camera hardware?"
            raise EnvironmentError, 'Halting program'
        if not self.CAMERA.LinkEnabled:
            print "... camera link DID NOT TURN ON; CANNOT CONTINUE"
            raise EnvironmentError, 'Halting program'
        # Define attributes
        self.dataPath  = None
        self.name      = 'SBIG'
        
    def exposeLight(self,length,filterSlot):
        print "Exposing light frame..."
        self.CAMERA.Expose(length,1,filterSlot)
        while not self.CAMERA.ImageReady:
            time.sleep(1)
        print "Light frame exposure and download complete!"
 
    def exposeDark(self,length,filterSlot):
        print "Exposing Dark frame..."
        self.CAMERA.Expose(length,0,filterSlot)
        while not self.CAMERA.ImageReady:
            time.sleep(1)
        print "Dark frame exposure and download complete!"
        
        
    def setFrame(self,opt,x,y,wx,wy):
        if opt == 'full':
            self.CAMERA.SetFullFrame()
            print "Camera set to full-frame mode"
        if opt == 'sub':
            self.CAMERA.StartX = x
            self.CAMERA.StartY = y
            self.CAMERA.NumX = wx
            self.CAMERA.NumY = wy
            print "Camera set to subframe. Note: Inputs must consider binning."
        else:
            print "Set opt to either 'full' or 'sub'"
        

    def setBinning(self,binmode):
        tup = (1,2,4)
        if binmode in tup:
            self.CAMERA.BinX = binmode
            self.CAMERA.BinY = binmode
            print "Camera binning set to %dx%d" % (binmode,binmode)
        else:
            print "ERROR: Invalid binning specified"


    def saveImage(self,filename):
        try:
            self.CAMERA.SaveImage(filename)
            print "saved file to ", filename
        except:
            print "Cannot save file"
            raise EnvironmentError, 'Halting program'


 
    def coolCCD(self,dt):
        if not self.CAMERA.CanSetTemperature:
            print "ERROR: cannot change temperature"
        elif self.CAMERA.CoolerOn:
            print "ERROR: Cooler already on."
        else:
            self.CAMERA.CoolerOn = True
            time.sleep(.5)
            ambTemp = self.CAMERA.Temperature
            self.CAMERA.TemperatureSetpoint = ambTemp - dt
            print "Cooling camera to ", str(dt), " C below " , str(ambTemp)
            print "Waiting for Cooler Power to Stabalize Below 50%"
            while self.CAMERA.CoolerPower > 50:
                time.sleep(1)

    def shutDown(self):
        if self.CAMERA.CoolerOn:
            # Warm up cooler
            if self.CAMERA.TemperatureSetpoint < self.CAMERA.AmbientTemperature:
                self.CAMERA.TemperatureSetpoint = self.CAMERA.AmbientTemperature
                print 'Warming Up CCD to Amb. Temp.'
                time.sleep(25)
            # Turn Cooler Off
            self.CAMERA.CoolerOn = False
        # Quit from camera, disconnect
        print 'Disconnecting and Quitting CAMERA'
        self.CAMERA.Quit()

                        

##
##    END OF 'cCamera' Class
##
