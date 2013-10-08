import pygame
import bluePoV


if not bluePoV.const.PY3:
    input = raw_input

# Varia el color regularmente
x,y = (480,64)
pendiente = 4

# Pygame inits & variables
pygame.init()
pygame.display.set_mode((x,y))

disp = pygame.display.get_surface()
clock = pygame.time.Clock()

# BluePoV init & variables
print ("Port? (default /dev/ttyUSB0)")
port = input()
if not port:
    port = "/dev/ttyUSB0"

sckt = bluePoV.SerialSocket()
sckt.connect(port,115200)

driver = bluePoV.Driver(sckt,[x,y],depth=1)

# Colores
r = 0
g = 255
b = 0

# # Pendientes
pR = pendiente
pG = 0
pB = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                quit()

    r += pR
    g += pG
    b += pB


    if 255 < r or r < 0 or 255 < g or g < 0 or 255 < b or b < 0:
        r = 255 if r >= 255 else 0
        g = 255 if g >= 255 else 0
        b = 255 if b >= 255 else 0

        pTemp = pB
        pB = -pG
        pG = -pR
        pR = -pTemp

    disp.fill([r,g,b])

    driver.pgBlit(disp)
    pygame.display.flip()


    clock.tick(10)
