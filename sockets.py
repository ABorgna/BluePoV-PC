#
# Banana banana banana
#
# ~ ABorgna
#

import constants as const

BLUETOOTH_AVAILABLE = False
SERIAL_AVAILABLE = False


if const.PY3:
    try:
        from socket import AF_BLUETOOTH
        AF_BLUETOOTH = None
        import socket
        BLUETOOTH_AVAILABLE = True
    except ImportError:
        pass
else:
    try:
        import bluetooth
        BLUETOOTH_AVAILABLE = True
    except ImportError:
        pass

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    pass

from warnings import warn
if not SERIAL_AVAILABLE and not BLUETOOTH_AVAILABLE:
    warn("Serial and bluetooth are not available",RuntimeWarning)

class BaseSocket(object):
    """
    Banana banana banana
    """
    def __init__(self):
        super(BaseSocket, self).__init__()
        self.timeout = None

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
    def __init__(self):
        super(BluetoothSocket, self).__init__()

        self.connected = False
        self.svSocket = None
        self.socket = None
        self.params = ()

    def connect(self, MACaddr, asServer=False, port=3, timeout=0.1):
        if not BLUETOOTH_AVAILABLE:
            raise RuntimeError("Bluetooth is not available")
        self.params = (MACaddr,asServer,port,timeout)

        self.close()
        self.asServer = asServer
        if self.asServer:
            if const.PY3:
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
            if const.PY3:
                self.socket = socket.socket(socket.AF_BLUETOOTH,
                                            socket.SOCK_STREAM,
                                            socket.BTPROTO_RFCOMM)
            else:
                self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((MACaddr,port))

        self.socket.settimeout(timeout)
        self.timeout = timeout
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

    def send(self,r):
        if type(r) == bytes:
            pass
        elif type(r) == int:
            r = bytes([r&0xff])
        elif type(r) == list:
            r = bytearray(r)
        elif type(r) == str:
            r = bytearray(r,'ascii')
        else:
            raise RuntimeError( "Serial data not supported \n"
                                +"    Type: "+str(type(r))+"\n"
                                +"    Value: "+str(r)
                               )

        try:
            return self.socket.send(r)
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
    def __init__(self):
        super(SerialSocket, self).__init__()

        self.socket = None
        self.params = ()

    def connect(self,port,bauds=9600,bytesize=8,parity='N',stopbits=1,timeout=0.01):
        if not SERIAL_AVAILABLE:
            raise RuntimeError("Serial is not available")
        self.params = (port,bauds,bytesize,parity,stopbits,timeout)
        self.close()
        self.socket = serial.Serial(port,bauds,bytesize,parity,stopbits,timeout)
        self.timeout = timeout

    def reconnect(self):
        if self.params:
            p = self.params
            self.connect(p[0],p[1],p[2],p[3],p[4],p[5])
        else:
            raise RuntimeError("Serial port not initialized")

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
        if type(r) == bytes:
            pass
        elif type(r) == int:
            r = bytes([r&0xff])
        elif type(r) == list:
            r = bytearray(r)
        elif type(r) == str:
            r = bytearray(r,'ascii')
        else:
            raise RuntimeError( "Serial data not supported \n"
                                +"    Type: "+str(type(r))+"\n"
                                +"    Value: "+str(r)
                               )

        try:
            return self.socket.write(r)
        except serial.SerialTimeoutException:
            return None

    def recv(self):
        a = self.socket.read(1)
        if a:
            return a[0]
        else:
            return None


