import pygame
import bluePoV


if not bluePoV.const.PY3:
    input = raw_input

# Varia el color regularmente
x,y = (480,32)
pendiente = 256

# Pygame inits & variables
pygame.init()
pygame.display.set_mode((x,y))

disp = pygame.display.get_surface()
clock = pygame.time.Clock()

# BluePoV init & variables
defPort = '/dev/ttyACM0'
print ("Port? (default "+defPort+")")
port = input()
if not port:
    port = defPort

print ("Bauds? (default 115200)")
bauds = input()
if not bauds:
    bauds = 115200

sckt = bluePoV.SerialSocket()
sckt.connect(port,bauds,timeout=0.01)

driver = bluePoV.Driver(sckt,[x,y],depth=1)

# Colores
r = 0
g = 255
b = 0

# # Pendientes
pR = pendiente
pG = 0
pB = 0

cnt = 0;

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
    pygame.display.flip()

    driver.pgBlit(disp)

    clock.tick(0.5)

# print("done!")
# s = input()

# while s != "q":
#     driver.pgBlit(disp)
#     print("Again?")
#    s = input()

