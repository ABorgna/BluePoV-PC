from sys import stdout
print("loading", end='')
stdout.flush()

import threading
import queue as queue
import socket

print(".", end='')
stdout.flush()

import pygame

print(".", end='')
stdout.flush()

import numpy
from numpy import ndarray as NumpyArray_t

"""

Todo esta detallado en 'README-esp.txt'.


Los paquetes son listas con 2 items;
    TKN - int
    DATA - int || list || NumpyArray_t

"""

class Transmitter ( threading.Thread ):
    """"
    The asynchronous communication thread
    """
    def __init__(self, deviceMac):
        super(Transmitter, self).__init__()

        # Status
        self.interlaced = 0 # Should send first even then odd columns
        self.depth = 1      # bits per color

        # Makes it stop when the program ends
        self.setDaemon ( True )

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
            packet = self.outQ.get(block=True)

            # Token
            self._send(packet[0]&0xFF)

            # Data
            if type(packet[1]) == NumpyArray_t:

                if packet[1].ndim not in (2,3):
                    # Wrong number of array dimensions
                    raise Exception("The dimensions are leaking!")

                # Interlaced transmission
                if self.interlaced:
                    xrang = list(range(0,len(packet[1])),2)
                    xrang += list(range(1,len(packet[1])),2)
                else:
                    xrang = range(len(packet[1]))


                for x in xrang:
                    for y in range(0,len(packet[1][0]),8):

                        for dep in range(self.depth):
                            mask = 0x80 >> dep

                            for color in range(3):
                                if packet[1].ndim == 3:
                                    # Each color in separated arrays
                                    msg = 0
                                    for shift in range(8):
                                        msg |= (packet[1][x][y+shift][color] & mask) \
                                                >> shift - dep
                                    self._send(msg)

                                else:
                                    # All the colors in the same int
                                    # Assuming 32-bit numbers
                                    msg = 0
                                    for shift in range(8):
                                        msg |= (packet[1][x][y+shift] & mask) \
                                                >> shift - dep + color*8 + 8
                                    self._send(msg)
            elif type(packet[1]) == list:
                for i in range(len(packet[1])):
                    self._send(packet[1][i]&0xFF)
            else:
                # Just a number
                self._send(packet[1]&0xFF)

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

        if resolution[1] % 8:
            raise Exception("The display height must be a multiple of 2")
        #self.arrayA = NumpyArray_t.(shape = (shape=(res[1],res[0]),dtype=numpy.int8)
        self.surfA = pygame.Surface(res)
        self.surfB = pygame.Surface(res)
        self.surfActive = 0;

        # Creates the transmitter and connects with the device
        self.transmitter = Transmitter(deviceMac)
        self.transmitter.run()

        # Set the resolution on the device
        self.setTotalWidth(res[0])
        self.setResolution(res)

    def _send_NoResp(self,packet,errorStr):
        """
        Sends the packet,
        throws an error if the response is not 0xffff
        """
        self.transmitter.send(packet)
        r = self.transmitter.recv()
        if r != 0xffff:
            raise Exception(errorStr.format(r))

    def store(self):
        self._send_NoResp((0x10,depth),"Error storing the display in ROM, {:#x}")

    def clean(self):
        self._send_NoResp((0x11,depth),"Error cleaning the display, {:#x}")

    def setResolution(self,res):
        # Height
        self._send_NoResp((0x14,res[1]),"Error setting the resolution, {:#x}")
        # Width
        self._send_NoResp((0x15,res[0]),"Error setting the resolution, {:#x}")

    def setDepth(self,depth):
        self._send_NoResp((0x16,depth),"Error setting the depth, {:#x}")

    def setTotalWidth(self,width):
        self._send_NoResp((0x17,depth),"Error setting the depth, {:#x}")



print ('hello')

