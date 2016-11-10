import time
import win32com.client
import logging

ERROR = True
NOERROR = False
 
 #http://www.rkblog.rk.edu.pl/w/p/ascom-end-user-application-developers/
 
##------------------------------------------------------------------------------
## Class: cTelescope
##------------------------------------------------------------------------------

__all__ =["cTelescope", "cLog", "cTeleOld","cMyT"]

class cTelescope:
    def __init__(self):
        print "Connecting to MaxIm DL..."
        #self.APPL = win32com.client.Dispatch("MaxIm.Application")
        self.APPL = win32com.client.Dispatch("TheSkyX.Application")
        self.__CHOOSER = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        self.__CHOOSER.DeviceType = 'Telescope'
        self.TELE = win32com.client.Dispatch("ASCOM.SoftwareBisque.Telescope") #make it __TELE once done testing       
        try:
            self.APPL.TelescopeConnected = True
        except:
            print "... cannot connect to telescope"
            print "--> Is telescope hardware attached?"
            raise EnvironmentError, 'Halting program'

    def slewCoord(self,RA,DEC):
        self.__TELE.SlewToCoordinates(RA,DEC)

    
class cLog:
    def __init__(self,logname):
        logger = logging.getLogger('TEL')  #eventually make this input and either camera or telescope depending on what's logging
        logger.setLevel(logging.DEBUG)
    
        # create file handler which logs even debug messages
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # add the handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        
        self.logger = logger
    
    def debug(self,message):
        self.logger.debug(message)
    
    def info(self,message):
        self.logger.info(message)
    
    def error(self,message):
        self.logger.error(message)
    
    def critiscal(self,message):
        self.logger.critical(message)


class cMyT:
    def __init__(self):
        print "Connecting to The Sky..."
        self.__APPL = win32com.client.Dispatch("TheSkyX.Application")
        self.__CHOOSER = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        self.__CHOOSER.DeviceType = 'Telescope'
        self.tel = win32com.client.Dispatch("ASCOM.SoftwareBisque.Telescope") #make it __TELE once done testing       
        if self.tel.Connected:
            print " ->Telescope was already connected"
        else:
            self.tel.Connected = True
        if self.tel.Connected:
            print " Connected to telescope now"
        else:
            print " Unable to connect to telescope, expect exception"

    def startup(self):
        # Unpark
        if self.tel.AtPark:
            if self.tel.CanUnpark:
                self.tel.Unpark()
                print 'Telescope Unparked'
            else:
                print 'Telescope cannot unpark'
        # Homing
        self.tel.FindHome()
        print '--> Finding Home position'

        # Tracking
        self.tel.Tracking = True
        if self.tel.Tracking:
            print " ->Telescope was already tracking"
        else:
            self.tel.Tracking = True
            print " Tracking now"
        if not self.tel.Tracking:
            print " Unable to begin tracking, expect exception"
        # Return position

    def goto(self,RA, DEC):
        """
        Go to RA DEC coordinates described in degrees
        """
        if self.tel.CanSlew:
            self.tel.SlewToCoordinates(RA,DEC)     # !!!pick coords currently in sky!
            print 'Slewing to RA: %s, DEC: %s' %(RA,DEC)
        else:
            print 'Warning: Cannot move axis. Did not slew'
        if self.tel.CanSync:
            pass #eventually sync? make sure star is in center?
        while(self.tel.Slewing):
            time.sleep(1)

    def getRA(self):
        return self.tel.RightAscension

    def getDEC(self):
        return self.tel.Declination
        
    def shutDown(self):
        # Park Telescope
        print 'Parking telescope'
        self.tel.Park()
        while not self.tel.AtPark:
            time.sleep(1)
        if self.tel.AtPark:
            print 'Telescope Parked'
        # Disconnect
        self.tel.Connected = False
        if not self.tel.Connected:
            print 'Disconnected from Telescope but not in the SkyX'



