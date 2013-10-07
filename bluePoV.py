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

from sys import version_info as SYS_V_INFO
if SYS_V_INFO[0] == 3: PY3 = True
SYS_V_INFO = None

from sockets import *
import constants as const

if PY3:
    import queue
else:
    import Queue as queue

import threading
from pygame import Surface,surfarray
import numpy as np
#from numpy import ndarray as NumpyArray_t
from time import sleep
from warnings import warn
from sys import stderr

import encoderSrc.encoder as encoder

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
        #self.buffer = NumpyArray_t.(shape = (shape=(res[1],res[0]),dtype=numpy.int8)
        self.buffer = Surface(res)

        # Creates the transmitter and connects with the device
        self.transmitter = Transmitter(socket)
        self.transmitter.start()

        # Set the resolution on the device
        self.setTotalWidth(res[0])
        self.setResolution(res)
        self.setDepth(depth)

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
                    warn(errorStr+", couldn't get response",UserWarning)
                    return None
            elif 0xffff > r >= 0xff00:
                warn(errorStr+", {:#x}".format(r),UserWarning)
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
        r = self._send((const.PING|const.GET,0x55),"Error when pinging")
        return r == 0x55

    def store(self):
        self._send((const.STORE|const.SET),"Error storing the display in ROM")

    def clean(self):
        self._send((const.CLEAN|const.SET),"Error cleaning the display")

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
        buffer = Surface(res)
        buffer.blit(self.buffer,(0,0))
        self.buffer = buffer

    def setDepth(self,depth):
        self.transmitter.txJoin()
        self._send((const.DEPTH|const.SET,depth),"Error setting the depth")

    def setTotalWidth(self,width):
        self._send((const.TOTAL_WIDTH|const.SET,width),"Error setting the total width")

    # Variable getters

    def getFPS(self):
        return self._send((const.FPS|const.GET),"Error getting the fps")

    def getResolution(self):
        # Height
        h = self._send((const.HEIGHT|const.GET),"Error getting the resolution")
        # Width
        w =self._send((const.WIDTH|const.GET),"Error getting the resolution")
        return (w,h)

    def getDepth(self):
        return self._send((const.DEPTH|const.GET),"Error getting the depth")

    def getTotalWidth(self):
        return self._send((const.TOTAL_WIDTH|const.GET),"Error getting the total width")

    # Data writers
    def blit(self,surface):
        if not self.buffer.get_locked():
            self.buffer.blit(surface,(0,0))
            self._send_noRcv([const.INTERLACED_BURST|const.DATA,
                              surfarray.pixels3d(self.buffer)])

    def blitColumn(self,surface,pos):
        if not self.buffer.get_locked():
            self.buffer.blit(surface,(pos,0))
            self._send_noRcv([const.WRITE_COLUMN|const.DATA,
                             pos,
                             surfarray.pixels3d(self.buffer)[pos:pos+1]])

    def blitSection(self,surface,pos,lenght):
        if not self.buffer.get_locked():
            self.buffer.blit(surface,(pos,0))
            self._send_noRcv([const.WRITE_SECTION|const.DATA,
                              pos,
                              lenght,
                              surfarray.pixels3d(self.buffer)[pos:pos+lenght]])








class Transmitter ( threading.Thread ):
    """"
    The asynchronous communication thread
    """
    def __init__(self,socket):
        super(Transmitter, self).__init__()

        # Status
        self.depth = 1          # bits per color
        self.height = 64        # column height

        # Makes it stop when the program ends
        self.setDaemon(True)

        # I/O queue
        self.inQ = queue.Queue(0)
        self.outQ = queue.Queue(0)

        # Where it connects with the display
        self.socket = socket

    def send(self,packet):
        """
        Queues a task to transmit
        """
        self.outQ.put(packet,block=True)

    def txJoin(self):
        """
        Waits for the transmitter to empty the out queue
        """
        self.outQ.join()

    def recv(self):
        """
        Gets the response of the last task
        (Blocking)
        """
        return self.inQ.get(block=True)

    def run (self):
        """
        Processes all the communication with the device
        """

        while True:
            # Check if connected, retry and warn every 1s
            tries = 1/self.socket.timeout
            while not self.socket.isConnected():
                self.socket.reconnect()
                sleep(0.1)
                tries -= 1
                if not tries:
                    tries = 1/self.socket.timeout
                    stderr.write("BluePoV not responding...")

            # Wait for tasks
            task = self.outQ.get(block=True)

            # Send everithing
            self._sendData(task)

            # Frees the references
            task = ()

            # ACK
            response = None
            r = self.socket.recv()
            if r != None:
                response = r << 8
            r = self.socket.recv()
            if r != None:
                response |= r
            self.inQ.put(response)

            # Mark as done and wait another
            self.outQ.task_done()


    def _sendData(self,task):
        # Send the appropriated bytes

        # Token
        token = task[0] & 0xff
        if token & const.DATA:
            token |= const.PRECODED
        self.socket.send(token)

        # Data

        # Special
        if task[0] == const.PING|const.GET:
            self.socket.send(task[1])
        elif task[0] == const.STORE|const.SET:
            pass
        elif task[0] == const.CLEAN|const.SET:
            pass
        # Setters
        elif task[0] == const.HEIGHT|const.SET:
            self.height = task[1];
            self.socket.send(task[1] >> 8)
            self.socket.send(task[1])
        elif task[0] == const.WIDTH|const.SET:
            self.socket.send(task[1] >> 8)
            self.socket.send(task[1])
        elif task[0] == const.DEPTH|const.SET:
            self.depth = task[1]
            self.socket.send(task[1])
        elif task[0] == const.TOTAL_WIDTH|const.SET:
            self.socket.send(task[1] >> 8)
            self.socket.send(task[1])
        # Getters
        elif task[0] == const.FPS|const.GET:
            pass
        elif task[0] == const.HEIGHT|const.GET:
            self.socket.send(task[1] >> 8)
            self.socket.send(task[1])
        elif task[0] == const.WIDTH|const.GET:
            self.socket.send(task[1] >> 8)
            self.socket.send(task[1])
        elif task[0] == const.DEPTH|const.GET:
            self.socket.send(task[1])
        elif task[0] == const.TOTAL_WIDTH|const.GET:
            self.socket.send(task[1] >> 8)
            self.socket.send(task[1])
        # Data
        elif task[0] == const.INTERLACED_BURST|const.DATA:
            # Encode the data

            frame = self._arrangePixels(task[1],interlaced=True)

            print("Sending data...")
            # self.socket.send(frame)
            print("done")
        elif task[0] == const.WRITE_COLUMN|const.DATA:
            # Send column number
            self.socket.send(task[1])
            # Encode the data
            frame = self._arrangePixels(task[2])
            self.socket.send(frame)
        elif task[0] == const.WRITE_SECTION|const.DATA:
            # Send first column number
            self.socket.send(task[1])
            # Send section lenght
            self.socket.send(task[2])
            # Encode the data
            frame = self._arrangePixels(task[3],lenght=task[2])
            self.socket.send(frame)

    def _arrangePixels(self,array,lenght = 0, interlaced = False):

        if array.ndim not in (2,3):
            # Bad number of array dimensions
            raise ValueError("The dimensions are leaking!")

        msg = array.flatten()
        respLen = int(len(msg)*self.depth/8)
        resp = np.empty((respLen),dtype=np.uint8)

        encoder.encodeRGB3d(msg,resp,self.depth,self.height)

        return resp
