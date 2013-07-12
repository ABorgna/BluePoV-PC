import threading
import Queue as queue
import socket

"""

Todo esta detallado en 'propuesta.txt'.


Los paquetes son listas con 3 items;
    TKN - char
    DATA - lista de chars
    ACK - int

"""

class BluePovThread ( threading.Thread ):
    """"
    The asynchronous communication thread
    """
    def __init__(self, deviceMac):
        super(BluePovThread, self).__init__()

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
            if packet != None:
                # Token
                self._send(packet[0]&0xFF)

                # Data
                for x in range(len(packet[1]))
                    if type(packet[1][i]) == list:
                        for i in range(len(packet[1]))

                    self._send(packet[1][i]&0xFF)

                # ACK
                response = None
                r = _recv()
                if not r == None:
                    reponse = r << 8
                r = _recv()
                if not r == None:
                    reponse |= r
                self.inQ.put(r)

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
    def __init__(self, deviceMac):
        super(BluePov, self).__init__()

        self.thread = BluePovThread(deviceMac)


print ('hello')

