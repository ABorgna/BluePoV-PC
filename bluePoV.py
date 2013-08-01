#
# Banana banana banana
#
# ~ ABorgna
#

#
# Todo esta detallado en 'README-esp.txt'.
#
#
# Los paquetes son listas con n items, n >= 2;
#     1er valor:  TKN - int
#     siguientes: DATA - int || list || NumpyArray_t

# Includes

from sockets import *

if PY3:
    import queue
else:
    import Queue as queue

import threading
from pygame import Surface,surfarray
#import numpy
from numpy import ndarray as NumpyArray_t
from time import sleep


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
            raise ValueError("The display height must be a multiple of 2")
        #self.buffer = NumpyArray_t.(shape = (shape=(res[1],res[0]),dtype=numpy.int8)
        self.buffer = Surface(res)

        # Creates the transmitter and connects with the device
        self.transmitter = Transmitter(socket)
        self.transmitter.start()

        # Set the resolution on the device
        self.setTotalWidth(res[0])
        self.setResolution(res)
        self.setDepth(depth)

    def _send(self,packet,errorStr,retries=5):
        """
        Sends the packet,
        waits for a valid response
        and checks the response for error codes (0xff00-0xfffe)
        """
        if retries >= 0:
            retries += 1
        while retries:
            retries -= 1
            self.transmitter.send(packet)
            r = self.transmitter.recv()
            if r == None:
                if not retries:
                    raise NullResponseError(errorStr+", couldn't get response")
            elif 0xffff > r >= 0xff00:
                raise BadResponseError(errorStr+", {:#x}".format(r))
            else
                return r

    def _send_noRcv(self,packet):
        """
        Sends the packet,
        doesn't wait for the operation to finish
        """
        self.transmitter.send(packet)

    # Special commands

    def ping(self):
        r = self._send((0x10,0x55),"Error when pinging")
        return r == 0x55

    def store(self):
        self._send((0x10),"Error storing the display in ROM")

    def clean(self):
        self._send((0x11),"Error cleaning the display")

    # Variable setters

    def setResolution(self,res):
        if res[1] % 8:
            raise ValueError("The display height must be a multiple of 2")

        self.transmitter.txJoin()
        # Height
        self._send((0x14,res[1]),"Error setting the resolution")
        # Width
        self._send((0x15,res[0]),"Error setting the resolution")

        # Resizes the buffer
        buffer = Surface(res)
        buffer.blit(self.buffer,(0,0))
        self.buffer = buffer

    def setDepth(self,depth):
        self.transmitter.txJoin()
        self._send((0x16,depth),"Error setting the depth")
        self.transmitter.depth = depth

    def setTotalWidth(self,width):
        self._send((0x17,width),"Error setting the total width")

    # Variable getters

    def getFPS(self):
        return self._send((0x01),"Error getting the fps")

    def getResolution(self):
        # Height
        h = self._send((0x04),"Error getting the resolution")
        # Width
        w =self._send((0x05),"Error getting the resolution")
        return (w,h)

    def getDepth(self):
        return self._send((0x06),"Error getting the depth")

    def getTotalWidth(self):
        return self._send((0x07),"Error getting the total width")

    # Data writers
    def blit(self,surface):
        self.buffer.blit(surface,(0,0))
        self._send_noRcv([0x83,surfarray.pixels3d(self.buffer)])

    def blitColumn(self,surface,pos):
        self.buffer.blit(surface,(pos,0))
        self._send_noRcv([0x80,pos,surfarray.pixels3d(self.buffer)[pos:pos+1]])

    def blitSection(self,surface,pos,lenght):
        self.buffer.blit(surface,(pos,0))
        self._send_noRcv([0x81,pos,lenght,surfarray.pixels3d(self.buffer)[pos:pos+lenght]])









class Transmitter ( threading.Thread ):
    """"
    The asynchronous communication thread
    """
    def __init__(self,socket):
        super(Transmitter, self).__init__()

        # Status
        self.depth = 1          # bits per color

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
        InterlacedTxOPCODE = 0x83

        while True:

            count = 0
            while not self.socket.isConnected():
                self.socket.reconnect()
                sleep(0.1)
                count += 1
                if count > 32:
                    count = 0
                    print("There seems to be a problem in the connection...")

            packet = self.outQ.get(block=True)

            # Token
            self.socket.send(packet[0]&0xFF)

            # Data
            for pktI in range (1,len(packet)):
                if type(packet[pktI]) == NumpyArray_t:

                    if packet[pktI].ndim not in (2,3):
                        # The dimensions are leaking!
                        raise ValueError("Wrong number of array dimensions")

                    # Interlaced transmission
                    if packet[0] == InterlacedTxOPCODE:
                        xrang = list(range(0,len(packet[pktI])),2)
                        xrang += list(range(1,len(packet[pktI])),2)
                    else:
                        xrang = range(len(packet[pktI]))

                    # Prevent the depth from being changed while transmitting
                    depth = self.depth

                    for x in xrang:
                        for y in range(0,len(packet[pktI][0]),8):

                            for dep in range(depth):
                                mask = 0x80 >> dep

                                for color in range(3):
                                    if packet[pktI].ndim == 3:
                                        # Each color in separated arrays
                                        msg = 0
                                        for shift in range(8):
                                            msg |= (packet[pktI][x][y+shift][color] & mask) \
                                                    >> shift - dep
                                        self.socket.send(msg)

                                    else:
                                        # All the colors in the same int
                                        # Assuming 32-bit numbers
                                        msg = 0
                                        for shift in range(8):
                                            msg |= (packet[pktI][x][y+shift] & mask) \
                                                    >> shift - dep + color*8 + 8
                                        self.socket.send(msg)
                else:
                    # A number, a list or a string
                    self.socket.send(packet[pktI])

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
