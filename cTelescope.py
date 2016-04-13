import time
import win32com.client
import logging

ERROR = True
NOERROR = False
 
 #http://www.rkblog.rk.edu.pl/w/p/ascom-end-user-application-developers/
 
##------------------------------------------------------------------------------
## Class: cTelescope
##------------------------------------------------------------------------------

__all__ =["cTelescope", "cLog", "cTeleOld"]

class cTelescope:
    def __init__(self):
        print "Connecting to MaxIm DL..."
        self.__APPL = win32com.client.Dispatch("MaxIm.Application")
        self.__CHOOSER = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        self.__CHOOSER.DeviceType = 'Telescope'
        self.__TELE = win32com.client.Dispatch("ASCOM.Celestron.Telescope")        
        try:
            self.__APPL.TelescopeConnected = True
        except:
            print "... cannot connect to telescope"
            print "--> Is telescope hardware attached?"
            raise EnvironmentError, 'Halting program'

class cLog:
    def __init__(self,logname):
        logger = logging.getLogger('camal')  #eventually make this input and either camera or telescope depending on what's logging
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
    

class cTeleOld:
    def __init__(self):
        # some random code from online          
        tel = win32com.client.Dispatch("ASCOM.Simulator.Telescope") 
        if tel.Connected:
            print "	->Telescope was already connected"
        else:
            tel.Connected = True
        if tel.Connected:
            print "	Connected to telescope now"
        else:
            print "	Unable to connect to telescope, expect exception"

        tel.Tracking = True
        tel.SlewToCoordinates(12.34, 86.7)     # !!!pick coords currently in sky!
        tel.Connected = False

