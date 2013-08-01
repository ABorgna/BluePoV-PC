import bluePoV
import pygame

if not bluePoV.PY3:
    input = raw_input

x,y = (16,16)
port = "/dev/ttyACM1"

sckt = bluePoV.SerialSocket()

sckt.connect(port,9600)

driver = bluePoV.Driver(sckt,[x,y],depth=1)

# pygame.init()
# pygame.display.set_mode((x,y))

# disp = pygame.display.get_surface()

# disp.fill([0,255,0])

# driver.blit(disp)
# pygame.display.flip()

input("Press any key... ")
