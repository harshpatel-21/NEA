import pygame,os,WINDOW
import pygame.freetype
pygame.init()

pygame.freetype.init()
x,y = WINDOW.x,WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

class Textbox:
    BACKGROUND = (120, 126, 214)
    BORDER = (35, 127, 200)
    HOVER = (126, 175, 252)
    TEXT_COLOR = (255, 255, 255)
    BORDER_HOVER = (255,255,255)
    background_color = BACKGROUND
    border_color = BORDER
    hover_color = HOVER
    text_color = TEXT_COLOR
    border_hover = BORDER_HOVER
    GREEN = (0,200,0)
    LARGE_FONT = pygame.font.SysFont('Sans', 35)
    MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)
    MEDIUM_FONT = pygame.font.SysFont('Sans', 25)
    SMALL_FONT = pygame.font.SysFont('Sans', 15)

    max_width = 270

    def __init__(self, x, y, text='', text_size='MEDIUM', text_color=text_color, padding=(0,0), size=(0,0),limit=True):
        self.padding=padding
        self.size=size
        self.text = text
        self.text_size = eval('self.' + text_size.upper()+'_FONT')
        self.x, self.y = x, y
        self.text_color = text_color
        self.limit = limit
        self.create_rect()

    def create_rect(self):
        padding_x, padding_y = self.padding
        w, h = self.size
        #updates the text to be displayed on the box
        self.font = self.text_size.render(self.text, True, pygame.Color(*self.text_color))
        tempRect = self.font.get_rect()
        tempRect.width = tempRect.width + padding_x
        if self.limit: tempRect.width = min(270,tempRect.width + padding_x)
        tempRect.height = tempRect.height + padding_y
        self.font_rect = tempRect
        self.rect = pygame.Rect(self.x,self.y,*self.font_rect.size)

        if w>0 and h>0:
            if self.font_rect.width - 43 < w:
                self.font_rect.width = w
            self.font_rect.height = h

        self.surface = pygame.Surface((self.font_rect.width, self.font_rect.height))
        self.background = self.background_color

    def show(self, canvas, center=False):
        pygame.draw.rect(self.surface, self.background, self.font_rect)
        pygame.draw.rect(self.surface, self.border_color, self.font_rect, 5)
        text_x = (self.font_rect.width - self.rect.width) // 2
        text_y = (self.font_rect.height - self.rect.height) // 2
        self.surface.blit(self.font, (text_x, text_y))
        
        if center == True:
            self.x = (canvas.get_width() - self.font_rect.width)//2

        canvas.blit(self.surface, (self.x, self.y))

    def set_properties(self, background=background_color,border=border_color,hover=hover_color):
        self.background = background
        self.border_color = border
        self.hover_color = hover

    def check_hover(self, mouse_pos=0):
        mouse_pos = pygame.mouse.get_pos()
        x = self.font_rect.copy()
        x.x = self.x
        x.y = self.y
        if x.collidepoint(mouse_pos):
            self.background = self.hover_color
        else:
            self.background = self.background_color

    def check_click(self, mouse_pos):
        x = self.font_rect.copy()
        x.x = self.x
        x.y = self.y
        return x.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])
