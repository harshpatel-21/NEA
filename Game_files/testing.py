import pygame,os,sys

x='\\'.join(os.path.abspath(__file__).split('\\')[:-2]) # allow imports from main folder
print(x)
sys.path.insert(1,x)

import pygame, re, json, WINDOW, math
from WINDOW import Display
from boxes import Textbox, Inputbox
from level_editor import load_level
from entity_class import Entity
from level_editor import load_level
from Game_V3 import Arrow

pygame.init()

FPS = 60
clock = pygame.time.Clock()
window = Display(new_window=True)

def main():
    img = pygame.image.load('images/Arrow04.png')
    a = img.get_width()
    b = img.get_height()
    img = pygame.transform.scale(img,(a*2,b*2))
    x1=x= 400
    y1=y= 200
    angle = 0
    acceleration = 5
    while True:
        window.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            # check for keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        # x,y = pygame.mouse.get_pos()

        angle = 180/math.atan(y1/x1)
        img_copy = pygame.transform.rotate(img,angle)
        center = (x1-(img_copy.get_width()/2),y1-(img_copy.get_height()/2))
        window.screen.blit(img_copy,center)
        pygame.display.update()

        x1+=2
        y1+=2

        clock.tick(FPS)
main()
