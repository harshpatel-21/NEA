import pygame
import pygame.freetype
import os, sys
pygame.init()
x,y = 50,80


os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

def get_path(path):
    absolute_path = os.path.abspath(path)
    if os.path.exists(absolute_path):
        return absolute_path
    else:
        return 0

class Display:
    RED = (255,0,0)
    BLUE = (0,0,255)
    WHITE = (255,255,255)
    GREY = (80,80,80)
    BLACK = (0,0,0)
    BACKGROUND = (70,70,70)
    ORANGE = (255,215,0)
    GREEN = BACKGROUND

    TILE_DIMENSION_X,TILE_DIMENSION_Y = 46,46
    BLOCKS_X,BLOCKS_Y = 28,15 # game window resolution
    WIDTH,HEIGHT = int(BLOCKS_X * TILE_DIMENSION_X), int(BLOCKS_Y * TILE_DIMENSION_Y)
    SIZE = (WIDTH, HEIGHT)

    MAX_BLOCKS_X = 112

    BIG_FONT = pygame.font.Font(None,35)
    MEDIUM_FONT = pygame.font.Font(None,25)
    MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)

    SMALL_FONT = pygame.font.Font(None,20)

    ARROW_X,ARROW_Y = 10,15 # default position of back arrow

    def __init__(self, background=GREEN, caption='Game',size=None,new_window=True,arrow_pos=None):
        if size is not None:
            self.SIZE = size
            self.width,self.height = size

        if arrow_pos is not None:
            self.ARROW_X, self.ARROW_Y = arrow_pos

        if new_window:
            self.screen = pygame.display.set_mode(self.SIZE)
            pygame.display.set_caption(caption)
        else:
            self.screen = pygame.Surface(self.SIZE)

        self.background=background


    def blit(self,content,coords):
        self.screen.blit(content,coords)

    def refresh(self,back=False,scroll=0):
        left_arrow = pygame.transform.scale(pygame.image.load(get_path('images/left-arrow.png')),(32,32))
        arrow_rect = pygame.Rect(self.ARROW_X,self.ARROW_Y,32,32)

        if isinstance(self.background,tuple): # if the background is an image
            self.screen.fill(self.background)

        else:
            # print(self.background)
            for i in range(4):
                self.screen.blit(self.background,((i*self.SIZE[0]) + scroll,0))

        if back: self.screen.blit(left_arrow,(self.ARROW_X,self.ARROW_Y))

    def check_return(self,mouse_pos=None):
        if not mouse_pos:
            mouse_pos = pygame.mouse.get_pos()
        left_arrow = pygame.transform.scale(pygame.image.load(get_path('images/left-arrow.png')),(32,32))
        arrow_rect = pygame.Rect(self.ARROW_X,self.ARROW_Y,32,32)

        if arrow_rect.collidepoint(mouse_pos): return 1

    def draw_text(self,text,pos,size='MEDIUM',color=WHITE):
        text = eval(f'self.{size.upper()}_FONT.render(text, True, color)')
        self.screen.blit(text,pos)

# class Canvas(Display):
#     def __init__(self, caption='Game',size=None, background=None, arrow_pos=None):
#         super().__init__(self,new_window=False,size=size, arrow_pos=arrow_pos)
#         pygame.display.set_caption(caption)

#         self.background = background

#         if background is None:
#             self.background = self.BLACK

#     # def refresh(self):
#     #     if isinstance(self.background,tuple):
#     #         self.screen.fill(self.background)
#     #     else:
#     #         self.screen.blit(self.background,(0,0))
