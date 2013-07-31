import bluePoV
import pygame

x,y = (16,16)
MAC = "00:13:03:18:04:60"

pygame.init()
pygame.display.set_mode((x,y))

s = pygame.display.get_surface()

driver = bluePoV.Driver([x,y],depth=1,asServer=False)

driver.connect(MAC)

s.fill([0,255,0])

driver.blit(s)
pygame.display.flip()

input("Press any key... ")
