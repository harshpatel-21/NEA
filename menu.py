import pygame, os, re, sys
import WINDOW
from QuestionWindow import DynamicBox
from boxes import Textbox
pygame.init()

x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)

def show_menu(username):
    padding1 = 20
    width1 = (window.WIDTH - (padding1*3))//3
    padding2 = 50
    width2 = (window.WIDTH - (padding2*2))//2
    row_1 = []
    text = ['Systems Architecture','Software and Software development','Exchanging Data']
    for i in range(3):
        row_1.append(DynamicBox(padding1*i+width1+padding1,270,(width1,0.2*width1),'topic',text=text[i]))
        pass
    while True:
        window.refresh(back=True,show_mouse_pos=True)
        if window.check_return():
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for box in row_1:
            box.show(window.screen)
        pygame.display.update()
        clock.tick(FPS)
show_menu('a')