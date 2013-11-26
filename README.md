The BluePov driver for PC
=========================

BluePoV is a persistence of vision display, 
just some leds rotating at ~2400rpm creating the illusion of a floating image, 
communicated over bluetooth with a pc or an android device.

This driver allows any program written in Python to send it a pixel matrix asynchronously,
and configure some variables.

The display, developed over 8 weeks, is the final project of Pio IX secondary school.


Requirements
------------

* Python 2 || 3, works under both.
* `numpy`.
* `cython`, if compiling the encoder.
* For now, only `pygame`'s surfaces are supported as the input data.

And depending on the communication method:
* Bluetooth works natively under python 3.2+, for py2 `pybuez` is needed.
* The serial port needs `pyserial` to work.

The bit-encoding part is written in C, so it must be compiled.
Under `encoderSrc/` there is a `setup.sh` and a `setup.bat`, use the appropriate.
They will try to compile for both the py2 and py3 versions.


Using it
--------

> There is an `example.py` with a simple setup and usage.
Also, there is [a drawing program](http://github.com/ABorgna/BluePoV-GUI) coded by my partner using it.

```python
# Everything is inside this module
import BluePoV
    
# Create a bluetooth or serial socket and connect to it
# sckt = bluePoV.BluetoothSocket()
# sckt.connect(MACaddr='12:34:56:78:9a:bc', asServer=False, port=3, timeout=0.1)
sckt = bluePoV.SerialSocket()
sckt.connect(port='/dev/ttyUSB0', bauds=9600, bytesize=8, parity='N', stopbits=1, timeout=0.01)
# Once connected, both sockets work equally

# Create the interface
# It will spawn a new thread, so we can send the data asynchronously
driver = bluePoV.Driver(socket=sckt, res=(480,64), depth=1)


# Now we can use it

# Check if it is connected
if driver.ping():
  echo('Yeah!')

# Clean the display
driver.clean()


# Refresh all the display
driver.pgBlit(pygameSurface)

# Or only part of it
driver.pgBlitSection(pygameSurface,pos=32,lenght=16)


# Change some parameters
driver.setResolution((240,128))
driver.setSpeed(0xf48)
driver.setDim(False)

# And get others
echo(driver.getFPS())
echo(driver.getDepth())

```
