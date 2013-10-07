import bluePoV
import pygame

if not bluePoV.PY3:
    input = raw_input

x,y = (480,64)
#port = "/dev/ttyACM0"
print ("Port? (default /dev/tty2)")
port = input()
if not port:
    port = "/dev/tty2"

sckt = bluePoV.SerialSocket()

sckt.connect(port,115200)

# sckt.send("\r\nTesting\r\n")
# sckt.send(65)

driver = bluePoV.Driver(sckt,[x,y],depth=1)

pygame.init()
pygame.display.set_mode((x,y))

disp = pygame.display.get_surface()

disp.fill([128,255,64])

driver.blit(disp)
pygame.display.flip()

input()
