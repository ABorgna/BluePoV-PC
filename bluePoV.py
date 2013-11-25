#
# Banana banana banana
#
# ~ ABorgna
#

#
# Explicacion en 'README-esp.txt'.
#
#
# Los paquetes son listas con n items, n >= 2;
#     1er valor:  FUNC - int
#     siguientes: DATA - int || list || NumpyArray_t

# Includes

import constants as const
from sockets import *
from transmitter import *

from pygame import Surface,surfarray
import numpy as np
#from numpy import ndarray as NumpyArray_t
from sys import stderr

class ResponseError(Exception):
    pass
class BadResponseError(ResponseError):
    pass
class NullResponseError(ResponseError):
    pass




class Driver(object):
    """
    Interface with the POV display
    """
    def __init__(self, socket, res, depth=1):
        super(Driver, self).__init__()

        # Variables
        self.resolution = res
        self.depth = depth

        # The array buffer
        if res[1] % 8:
            raise ValueError("The display height must be a multiple of 8")

        # Image buffer, the data to transmit
        self.buffer = np.empty((res[0],res[1],3),dtype=np.uint8)

        # Creates the transmitter and connects with the device
        self.transmitter = Transmitter(socket)
        self.transmitter.start()

        # Set the resolution on the device
        self.setTotalWidth(res[0])
        self.setResolution(res)
        self.setDepth(depth)
        self.setDimm(0)

    def _send(self,packet,errorStr="Transmission error",retries=0):
        """
        Sends the packet
        and checks the response for error codes (0xff00-0xfffe)
        Response:
            >= 0 - Response
             < 0 - Error
            None - No response
        """
        if retries >= 0:
            retries += 1
        while retries:
            retries -= 1
            self.transmitter.send(packet)
            r = self.transmitter.recv()
            if r == None:
                if not retries:
                    stderr.write(errorStr+", couldn't get response")
                    return None
            elif 0xffff > r >= 0xff00:
                stderr.write(errorStr+", {:#x}".format(r))
                return -r
            else:
                return r

    def _send_noRcv(self,packet):
        """
        Sends the packet,
        doesn't wait for the operation to finish
        """
        self.transmitter.send(packet)

    # Special commands

    def ping(self):
        r = self._send((const.PING|const.GET,),"Error when pinging")
        return r == 0x55

    def store(self):
        self._send((const.STORE|const.SET,),"Error storing the display in ROM")

    def clean(self):
        self._send((const.CLEAN|const.SET,),"Error cleaning the display")

    # Variable setters

    def setResolution(self,res):
        if res[1] % 8:
            raise ValueError("The display height must be a multiple of 8")

        self.transmitter.txJoin()
        # Height
        self._send((const.HEIGHT|const.SET,res[1]),"Error setting the resolution")
        # Width
        self._send((const.WIDTH|const.SET,res[0]),"Error setting the resolution")

        # Resizes the buffer
        buffer = np.empty((res[0],res[1],3),dtype=np.uint8)
        buffer[0:len(self.buffer)] = self.buffer
        self.buffer = buffer

    def setDepth(self,depth):
        self.transmitter.txJoin()
        self._send((const.DEPTH|const.SET,depth),"Error setting the depth")

    def setTotalWidth(self,width):
        self._send((const.TOTAL_WIDTH|const.SET,width),"Error setting the total width")

    def setSpeed(self,s):
        self._send((const.SPEED|const.SET,s),"Error setting the speed")

    def setDimm(self,s):
        self._send((const.DIMM|const.SET,s),"Error setting the dimm")

    # Variable getters

    def getFPS(self):
        return self._send((const.FPS|const.GET,),"Error getting the fps")

    def getResolution(self):
        # Height
        h = self._send((const.HEIGHT|const.GET,),"Error getting the resolution")
        # Width
        w =self._send((const.WIDTH|const.GET,),"Error getting the resolution")
        return (w,h)

    def getDepth(self):
        return self._send((const.DEPTH|const.GET,),"Error getting the depth")

    def getTotalWidth(self):
        return self._send((const.TOTAL_WIDTH|const.GET,),"Error getting the total width")

    def getSpeed(self):
        return self._send((const.SPEED|const.GET,),"Error getting the speed")

    def getDimm(self):
        return self._send((const.DIMM|const.GET,),"Error getting the dimm")

    # Pygame data writers
    def pgBlit(self,surface):
        # Copy the matrix as a numpy array
        self.buffer = np.copy(surfarray.pixels3d(surface).flatten())

        # Is there isn't already a burst task in the queue, create one
        if not self.transmitter.burstInQueue.isSet():
            self.transmitter.burstInQueue.set()
            self._send_noRcv([const.BURST|const.DATA, self.buffer])

    def pgBlitColumn(self,surface,pos):
        # Copy the column to a numpy array
        self.buffer[pos:pos+1] = np.copy(surfarray.pixels3d(surface).flatten())

        # Is there isn't already a burst task in the queue, create a write_column task
        if not self.transmitter.burstInQueue.isSet():
            self._send_noRcv([const.WRITE_COLUMN|const.DATA, pos, self.buffer[pos:pos+1]])

    def pgBlitSection(self,surface,pos,lenght):
        # Copy the section to a numpy array
        self.buffer[pos:pos+lenght] = np.copy(surfarray.pixels3d(surface).flatten())

        # Is there isn't already a burst task in the queue, create a write_section task
        if not self.transmitter.burstInQueue.isSet():
            self._send_noRcv([const.WRITE_SECTION|const.DATA, pos, lenght,
                              self.buffer[pos:pos+lenght]])
        self.setTotalWidth(res[0])
