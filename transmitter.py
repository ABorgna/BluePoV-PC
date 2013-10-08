#
# Banana banana banana
#
# ~ ABorgna
#

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

            self.socket.send(frame)
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

        return resp.tolist()
