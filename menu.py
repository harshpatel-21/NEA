import pygame, os, re, sys
import WINDOW
from QuestionWindow import DynamicBox
from boxes import Textbox
from entity_class import BoxGroup
pygame.init()

x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)

def show_menu(username):
    width1 = 402
    padding1 = (window.WIDTH-3*width1)//4
    topics = []
    row_1 = ['Systems Architecture', 'Software and Software development', "Exchanging Data"]
    row_2 = ['Data types, Data structures, and Algorithms', 'Elements of Computational thinking, Problem solving, and programming']
    for i in range(3):
        topics.append(DynamicBox(padding1*i+(width1*i)+padding1,200,(width1,0.4*width1),'topic',text=row_1[i]))

    width2=500
    padding2 = (window.WIDTH-2*width2)//3
    for j in range(2):
        topics.append(DynamicBox(padding2*j+(width2*j)+padding2,topics[1].rect.h+200+padding1,(width2,0.35*width2),'topic',text=row_2[j]))
    topics = BoxGroup(*topics)
    while True:
        window.refresh(back=True,show_mouse_pos=True)
        if window.check_return():
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = topics.check_clicks()
                if clicked:
                    print(clicked.text)

        topics.update_boxes(window.screen)
        pygame.display.update()
        clock.tick(FPS)

if __name__ == '__main__':
    show_menu('a')