import pygame,os,WINDOW
import pygame.freetype
pygame.init()

pygame.freetype.init()
x,y = WINDOW.x,WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
Display = WINDOW.Display
class Textbox:
    rect: object
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

    def __init__(self, x, y, text='', text_size='MEDIUM', text_color=text_color, padding=(10,10), size=(0,0),limit=True):
        self.padding = padding
        self.size = size
        self.text = text
        self.text_size = eval('self.' + text_size.upper()+'_FONT')
        self.x, self.y = x, y
        self.text_color = text_color
        self.limit = limit
        self.create_rect()

    def create_rect(self):
        padding_x,padding_y = self.padding

        w,h=self.size

        #updates the text to be displayed on the box
        self.font = self.text_size.render(self.text, True, pygame.Color(*self.text_color))

        self.rect = self.font.get_rect() # this is the font rectangle
        tempRect = self.rect.copy()
        tempRect.width = tempRect.width + padding_x
        if self.limit:
            tempRect.width = min(270,tempRect.width +padding_x)
        tempRect.height = tempRect.height + padding_y
        self.main_rec = tempRect # font rectangle with padding, the outside rectangle

        if w>0 and h>0:
            if self.main_rec.width - 43 < w:
                self.main_rec.width = w
            self.main_rec.height = h

        self.surface = pygame.Surface((self.main_rec.width, self.main_rec.height))
        self.background = self.background_color
        # self.main_rec.topleft = (self.x,s/elf.y)


    def show(self, canvas, center=False):
        pygame.draw.rect(self.surface, self.background, self.main_rec)
        pygame.draw.rect(self.surface, self.border_color, self.main_rec, 5)
        text_x = (self.main_rec.width - self.rect.width) // 2
        text_y = (self.main_rec.height - self.rect.height) // 2
        self.surface.blit(self.font, (text_x, text_y))

        if center:
            self.x = (canvas.get_width() - self.main_rec.width)//2 # center it

        canvas.blit(self.surface, (self.x, self.y)) # blitting the box at the initially specified x and y position

    def set_properties(self, background=background_color, border=border_color, hover=hover_color):
        self.background = background
        self.border_color = border
        self.hover_color = hover

    def check_hover(self,mouse_pos=0):
        mouse_pos = pygame.mouse.get_pos()
        x=self.main_rec.copy()
        x.x = self.x
        x.y = self.y
        if x.collidepoint(mouse_pos):
            self.background = self.hover_color
        else:
            self.background = self.background_color

    def check_click(self,mouse_pos=None):
        x=self.main_rec.copy()
        x.x = self.x
        x.y = self.y
        return x.collidepoint(pygame.mouse.get_pos()) and (pygame.mouse.get_pressed()[0])


class Inputbox(Textbox):
    def __init__(self, x, y, text='',text_size='medium',padding=(0,0),size=(0,0),limit=True):
        super().__init__(x,y,text=text,text_size=text_size,padding=padding,size=size,limit=limit)


# noinspection PyArgumentList
class DynamicBox(Textbox):
    LARGE_FONT = pygame.font.SysFont('Sans', 35)
    MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)
    MEDIUM_FONT = pygame.font.SysFont('Sans', 25)
    SMALL_FONT = pygame.font.SysFont('Sans', 15)

    incorrect_color = (204, 51, 0)
    correct_color = (51, 153, 51)

    def __init__(self, x, y, size, obj_type, text='', font_size='MEDIUM',center_text=True):
        if isinstance(font_size, int):
            self.font = pygame.font.SysFont('Sans', font_size)

        elif font_size in 'MEDIUM LARGE MEDLARGE SMALL':
            self.font = eval(f'self.{font_size}_FONT')

        self.obj_type = obj_type
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, *size)
        self.surface = pygame.Surface(self.rect.size)
        self.background = Textbox.BACKGROUND
        text_rect_size = [*map(lambda i: i*0.9,self.rect.size)] # create a padding for where the text will be placed

        # calculate the offset to place the text rectangle in the center of the main box rectangle
        dx = (self.rect.w - text_rect_size[0])//2
        dy = (self.rect.h - text_rect_size[1])//2
        self.text_rect = pygame.Rect((self.rect.x + dx, self.rect.y + dy, *text_rect_size))
        self.surf = None
        self.text=text
        self.center_text = center_text
        self.border_color = None
        self.add_text(text)

    def show(self, surface):
        # self.surface.fill(self.background)
        pygame.draw.rect(self.surface, self.background, (0, 0, self.rect.w, self.rect.h))
        if self.border_color: # if there is a border color
            pygame.draw.rect(self.surface, self.border_color, (0, 0, self.rect.w, self.rect.h), 1)
        # pygame.draw.rect(self.surface, self.border_color, (self.text_rect.x-self.rect.x, self.text_rect.y-self.rect.y, self.text_rect.w,self.text_rect.h),1)
        surface.blit(self.surface, self.rect.topleft)
        if self.surf:
            # pygame.draw.rect(surface,(255,0,0),(self.rect.x + (self.rect.w-self.text_rect.w)//2, self.rect.y + (self.rect.h-self.text_rect.h)//2, self.text_rect.w, self.text_rect.h),1)
            if not self.center_text: surface.blit(self.surf, self.text_rect.topleft)
            else: surface.blit(self.surf, (self.rect.x + (self.rect.w-self.text_rect.w)//2, self.rect.y + (self.rect.h-self.text_rect.h)//2, self.text_rect.w, self.text_rect.h))

    # this allows text to fit in a specified box.
    def add_text(self, text, delay=False):
        """
        \\n = newline
        break up the text and try to blit each word individually; if at any point any of the letters for a word goes out,
        then repeat the blit attempt process for the word again but on a new line/y-coordinate. However, if there is only
        one word (left in the text) and it doesn't fit, trying to add to a new y value would cause the same issue, therefore
        if this does occur, don't try to add that word forever, just break out of the loop and if the word is missing, the user
        should know that it couldn't fit in the box.
        """
        text = text.split() # split all the words
        # modification variables
        add_y = 0
        widths = 0
        # text variables
        pointer = 0
        letter_count = 0
        height = self.font.render('h',1,(255,255,255)).get_height()
        self.surf = pygame.Surface(self.text_rect.size, pygame.SRCALPHA, 32)
        self.surf.convert_alpha()

        if self.obj_type == 'button' and len(text)==1:
            rendered = self.font.render(text[0],1,(255,255,255))
            self.surf.blit(rendered,(0,0))
            return

        # to evaluate: this can go on forever if the box is too small for all of the text to fit in
        break_while = False
        y_increment = 0
        max_x = 0
        while pointer <= len(text) - 1:
            current_word = text[pointer]
            if y_increment > 2: # if 2 new line attempts have been made then it means the word still cannot fit
                # break out of the while loop and stop attempting to infinitely trying to add the word
                break
            temp = self.surf.copy() # create a temporary surface where letters will be blitted
            font_letters = []

            for letter in current_word:
                font_letters += [self.font.render(letter, 1, (255, 255, 255))]

            for index,letter in enumerate(font_letters): # iterating through each rendered letter
                newline = False

                rect = letter.get_rect()
                if not letter_count: # if the row has no letters (if its the first letter)
                    proposed_x, proposed_y = 0, add_y * height
                    letter_count += 1
                    widths = 0 # initial padding from the side of rectangle
                else:
                    proposed_x = widths # sum all the widths + padding of previous letters
                    proposed_y = add_y * height
                    # if adding a character of a word will overflow, add the whole word to the next line
                    if proposed_x + rect.w > self.text_rect.w:
                        newline = True

                if newline or current_word == '\\n':
                    max_x = max(max_x, min(self.text_rect.w, proposed_x+rect.w))
                    add_y += 1 # increasing the y
                    widths = 1 # resetting the widths to 1
                    letter_count = 0 # reset the letter count on the row
                    if pointer == len(text)-1: # if its the last word and still not fitting
                        y_increment += 1
                    if current_word == '\\n':
                        pointer += 1
                    break # repeat the process again for this word but on a new line
                max_x = max(max_x, min(self.text_rect.w, proposed_x+rect.w))

                temp.blit(letter, (proposed_x, proposed_y)) # blit it on the temp surface
                widths += rect.w + 1 # +1 is for the padding between letters

            else: # if the loop finished iterating meaning that all letters were successfully blitted
                if letter_count: # if there is a first character on the row
                    # self.surf.blit(self.font.render('   ',1,(255,255,255)), (proposed_x, proposed_y))
                    widths += self.font.render(' ',1,(255,255,255)).get_width()# this is the "space" between each word
                pointer += 1 # once a word has finished blitting, move onto the next one
                self.surf = temp.copy() # if a word was fully blitted, then add it onto the main canvas/surface of this box

        self.text_rect.h = (add_y+1) * font_letters[0].get_height()
        self.text_rect.w = max_x

    def check_hover(self, mouse_pos=0):
        # if the mouse position is over the rectangle, change color, otherwise change it back to normal
        if self.obj_type != 'question':
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.background = self.hover_color
                self.border_color = (0, 0, 255)
            else:
                self.background = self.background_color
                self.border_color = None

    def check_click(self, mouse_pos=0):
        if self.obj_type != 'question':
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0]):
                return self


class BoxGroup:
    def __init__(self, *args):
        self.objects = [*args]

    def update_boxes(self, surface):
        obj = False
        for box in self.objects:
            if hasattr(box, 'show'):
                box.show(surface)
            if hasattr(box, 'check_hover'):
                box.check_hover()
            if hasattr(box, 'check_click') and not obj:  # if a box hasn't already been clicked
                if box.check_click():
                    obj = box

    def set_background(self, color):
        pass

    def check_clicks(self):
        obj = False
        for box in self.objects:
            if hasattr(box, 'check_click') and not obj:
                if box.check_click():
                    obj = box
        return obj

    def get_list(self):
        return self.objects