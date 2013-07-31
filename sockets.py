#
# Banana banana banana
#
# ~ ABorgna
#

PY3 = False
BLUETOOTH_AVAILABLE = False
SERIAL_AVAILABLE = False


from sys import version_info as SYS_V_INFO
if SYS_V_INFO[0] == 3: PY3 = True
SYS_V_INFO = None

if PY3:
    try:
        from socket import AF_BLUETOOTH
    except importException:
        pass
    finally:
        AF_BLUETOOTH = None
        import socket
        BLUETOOTH_AVAILABLE = True
else:
    try:
        import bluetooth
    except importException:
        pass
    finally:
        BLUETOOTH_AVAILABLE = True

try:
    import serial
except importException:
    pass
finally:
    SERIAL_AVAILABLE = True


class BaseSocket(object):
    """
    Banana banana banana
    """
    def __init__(self, arg):
        super(BaseSocket, self).__init__()

    def connect(self):
        pass

    def reconnect(self):
        pass

    def close(self):
        pass

    def isConnected(self):
        return False

    def send(self,r):
        pass

    def recv(self):
        """
        Returns one byte or None
        """
        return None




class BluetoothSocket(BaseSocket):
    """
    Banana banana banana
    """
    def __init__(self, arg):
        super(BluetoothSocket, self).__init__()

        self.connected = False
        self.svSocket = None
        self.socket = None
        self.params = []

    def connect(self, MACaddr, asServer=False, port=3, timeout=1):
        if not BLUETOOTH_AVAILABLE:
            raise Exception("Bluetooth is not available")
        self.params = [MACaddr,asServer,port,timeout]

        self.close()
        self.asServer = asServer
        if self.asServer:
            if PY3:
                self.svSocket = socket.socket(socket.AF_BLUETOOTH,
                                              socket.SOCK_STREAM,
                                              socket.BTPROTO_RFCOMM)
            else:
                self.svSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.svSocket.bind((MACaddr,port))
            self.svSocket.listen(1)
            self.socket,clientinfo = self.svSocket.accept()
            self.svSocket.settimeout(timeout)
        else:
            if PY3:
                self.socket = socket.socket(socket.AF_BLUETOOTH,
                                            socket.SOCK_STREAM,
                                            socket.BTPROTO_RFCOMM)
            else:
                self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((MACaddr,port))

        self.socket.settimeout(timeout)
        self.connected = True

    def reconnect(self):
        if self.params:
            p = self.params
            self.connect(p[0],p[1],p[2],p[3])

    def close(self):
        if not self.isConnected():
            return
        if self.svSocket != None:
            self.svSocket.shutdown()
            self.svSocket.close()
            self.svSocket = None
        if self.socket != None:
            self.socket.shutdown()
            self.socket.close()
            self.socket = None
        self.connected = False

    def isConnected(self):
        return self.connected

    def send(self,data):
        try:
            return self.socket.send(byte(data))
        except socket.timeout:
            self.connected = False
            return None

    def recv(self):
        try:
            return self.socket.recv(1)[0]
        except socket.timeout:
            return None




class SerialSocket(BaseSocket):
    """
    Banana banana banana
    """
    def __init__(self, arg):
        super(BluetoothSocket, self).__init__()

        self.socket = None
        self.params = []

    def connect(self,port,bauds=9600,bytesize=8,parity='N',stopbits=1,timeout=1):
        if not SERIAL_AVAILABLE:
            raise Exception("Serial is not available")
        self.params = [port,bauds,bytesize,parity,stopbits,timeout]
        self.close()
        self.socket = serial.Serial(port,bauds,bytesize,parity,stopbits,timeout)

    def reconnect(self):
        if self.params:
            p = self.params
            self.connect(p[0],p[1],p[2],p[3],p[4],p[5])

    def close(self):
        if not self.isConnected():
            return
        self.socket.close()

    def isConnected(self):
        if self.socket != None:
            return self.socket.isOpen()
        else:
            return False

    def send(self,r):
        try:
            return self.socket.write(byte(r)) # Catch exception?
        except Exception:
            return None

    def recv(self):
        a = self.socket.read(1)
        if a:
            return a[0]
        else:
            return None


