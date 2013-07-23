print("loading...")

from sys import version_info as SYS_V_INFO
PY3 = False
if SYS_V_INFO[0] == 3: PY3 = True

if PY3: import queue
else: import Queue as queue
import threading
import socket
import pygame
import numpy
from numpy import ndarray as NumpyArray_t

print("done!")

"""

Todo esta detallado en 'README-esp.txt'.


Los paquetes son listas con n items, n >= 2;
    1er valor:  TKN - int
    siguientes: DATA - int || list || NumpyArray_t

"""

class Transmitter ( threading.Thread ):
    """"
    The asynchronous communication thread
    """
    def __init__(self, deviceMac):
        super(Transmitter, self).__init__()

        # Status
        self.depth = 1          # bits per color

        # Makes it stop when the program ends
        self.setDaemon(True)

        # I/O queue
        self.inQ = queue.Queue(0)
        self.outQ = queue.Queue(0)

        # Where it connects with the display
        self.socket = socket.socket(socket.AF_BLUETOOTH,
                                    socket.SOCK_STREAM,
                                    socket.BTPROTO_RFCOMM)
        self.socket.connect((deviceMac, 1))
        self.socket.settimeout(0.1)

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
        IntelacedTxOPCODE = 0x83

        while True:
            packet = self.outQ.get(block=True)

            # Token
            self._send(packet[0]&0xFF)

            # Data
            for pktI in range (1,len(packet)):
                if type(packet[pktI]) == NumpyArray_t:

                    if packet[pktI].ndim not in (2,3):
                        # Wrong number of array dimensions
                        raise Exception("The dimensions are leaking!")

                    # Interlaced transmission
                    if packet[0] == IntelacedTxOPCODE:
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
                                        self._send(msg)

                                    else:
                                        # All the colors in the same int
                                        # Assuming 32-bit numbers
                                        msg = 0
                                        for shift in range(8):
                                            msg |= (packet[pktI][x][y+shift] & mask) \
                                                    >> shift - dep + color*8 + 8
                                        self._send(msg)
                elif type(packet[pktI]) == list:
                    for i in range(len(packet[pktI])):
                        self._send(packet[pktI][i]&0xFF)
                else:
                    # Just a number
                    self._send(packet[pktI]&0xFF)

            # ACK
            response = None
            r = _recv()
            if not r == None:
                reponse = r << 8
            r = _recv()
            if not r == None:
                reponse |= r
            self.inQ.put(reponse)

            # Mark as done and wait another
            self.outQ.task_done()

    def _send(self,data):
        """
        Sends data to the device
        """
        return self.socket.send(byte(data))

    def _recv(self):
        """
        Receives data from the device,
        returns the data or None if reached the timeout
        """
        try:
            return self.socket.recv(1)[0]
        except socket.timeout:
            return None


class BluePov(object):
    """
    Interface with the POV display
    """
    def __init__(self, deviceMac, res, depth=1):
        super(BluePov, self).__init__()

        # State variables
        preview = False

        # The array buffer
        if res[1] % 8:
            raise Exception("The display height must be a multiple of 2")
        #self.buffer = NumpyArray_t.(shape = (shape=(res[1],res[0]),dtype=numpy.int8)
        self.buffer = pygame.Surface(res)

        # Creates the transmitter and connects with the device
        self.transmitter = Transmitter(deviceMac)
        self.transmitter.start()

        # Set the resolution on the device
        self.setTotalWidth(res[0])
        self.setResolution(res)

    def _send(self,packet,errorStr):
        """
        Sends the packet,
        checks the response for error codes (0xff00-0xfffe)
        """
        self.transmitter.send(packet)
        r = self.transmitter.recv()
        if 0xffff > r >= 0xff00:
            raise Exception(errorStr.format(r))
        return r

    def _send_noRcv(self,packet):
        """
        Sends the packet,
        doesn't wait for the operation to finish
        """
        self.transmitter.send(packet)

    # Special commands

    def ping(self):
        r = self._send((0x10,0x55),"Error when pinging, {:#x}")
        return r == 0x55

    def store(self):
        self._send((0x10),"Error storing the display in ROM, {:#x}")

    def clean(self):
        self._send((0x11),"Error cleaning the display, {:#x}")

    # Variable setters

    def setResolution(self,res):
        self.transmitter.txJoin()
        # Height
        self._send((0x14,res[1]),"Error setting the resolution, {:#x}")
        # Width
        self._send((0x15,res[0]),"Error setting the resolution, {:#x}")
        # Resizes the buffers
        buffer = pygame.Surface(res)
        buffer.blit(self.buffer,(0,0))
        self.buffer = surfA

    def setDepth(self,depth):
        self.transmitter.txJoin()
        self._send((0x16,depth),"Error setting the depth, {:#x}")
        self.transmitter.depth = depth

    def setTotalWidth(self,width):
        self._send((0x17,width),"Error setting the total width, {:#x}")

    # Variable getters

    def getFPS(self):
        return self._send((0x01),"Error getting the fps, {:#x}")

    def getResolution(self):
        # Height
        h = self._send((0x04),"Error getting the resolution, {:#x}")
        # Width
        w =self._send((0x05),"Error getting the resolution, {:#x}")
        return (w,h)

    def getDepth(self):
        return self._send((0x06),"Error getting the depth, {:#x}")

    def getTotalWidth(self):
        return self._send((0x07),"Error getting the total width, {:#x}")

    # Data writers
    def flip(self,surface):
        self.buffer.blit(surface,(0,0))
        self._send_noRcv([0x83,pygame.surfarray.pixels3d(self.buffer)])

    def flipColumn(self,surface,pos):
        self.buffer.blit(surface,(pos,0))
        self._send_noRcv([0x80,pos,pygame.surfarray.pixels3d(self.buffer)[pos:pos+1]])

    def flipSection(self,surface,pos,lenght):
        self.buffer.blit(surface,(pos,0))
        self._send_noRcv([0x81,pos,lenght,pygame.surfarray.pixels3d(self.buffer)[pos:pos+lenght]])


print ('hello')

