import bluePoV
import pygame

x,y = (480,64)
MAC = "00:00:00:00:00:00"

pygame.init()
pygame.display.set_mode((x,y))

s = pygame.display.get_surface()

driver = bluePoV.Driver([x,y],depth=1,asServer=True)

#driver.connect(MAC)

s.fill([0,255,0])

driver.blit(s)
pygame.display.flip()

input("Press any key... ")
