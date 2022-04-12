import pygame
import pygame.freetype
import os, sys, json, re

x,y = 50,80


os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
from _ctypes import PyObj_FromPtr  # see https://stackoverflow.com/a/15012814/355230 for adding lists to json no indent

# --------------- modules to add lists/tuples to .json without indentation ---------------------- #
class NoIndent(object):
    """ Value wrapper. """
    def __init__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError('Only lists and tuples can be wrapped')
        self.value = value

class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'  # Unique string pattern of NoIndent object ids.
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))  # compile(r'@@(\d+)@@')

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {'cls', 'indent'}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super(MyEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                    else super(MyEncoder, self).default(obj))

    def iterencode(self, obj, **kwargs):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super(MyEncoder, self).iterencode(obj, **kwargs):
            match = self.regex.search(encoded)
            if match:
                id = int(match.group(1))
                no_indent = PyObj_FromPtr(id)
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched id string with json formatted representation
                # of the corresponding Python object.
                encoded = encoded.replace(
                            '"{}"'.format(format_spec.format(id)), json_repr)

            yield encoded

def get_path(path):
    absolute_path = os.path.abspath(path)
    if os.path.exists(absolute_path):
        return absolute_path
    else:
        return 0

def read_json(path):
    details = get_path(path)
    with open(details, 'r') as file:
        return json.load(file)

def write_json(data, path, cls=MyEncoder):
    details_path = get_path(path)

    # re-assigning any lists to NoIndent instances
    for detail in data:
        for thing in data[detail]:
            if type(data[detail][thing]) == list and thing!='options': # so options can be visually seen
                data[detail][thing] = NoIndent(data[detail][thing]) # if its any other thing that's list format, ie points or right-wrong

    with open(details_path, 'w') as file:
        file.seek(0)
        json.dump(data, file, indent=4, cls=cls)

def delete_json_key(path, cls=MyEncoder, key=None, two_d=False):
    details_path = get_path(path)
    data = read_json(details_path)
    for key1 in data:
        if two_d:
            for key2 in data[key1]:
                if key2 == key:
                    del data[key1][key2]
                    break # go onto next main key
        else:
            if key1==key:
                del data[key1]
                break

    write_json(data, path)



class Display:
    pygame.init()
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

    LARGE_FONT = pygame.font.SysFont('Sans', 35)
    MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)
    MEDIUM_FONT = pygame.font.SysFont('Sans', 25)
    SMALL_FONT = pygame.font.SysFont('Sans', 20)

    ARROW_X, ARROW_Y = 10, 15 # default position of back arrow

    def __init__(self, background=GREEN, caption='Game', size=SIZE, new_window=True, arrow_pos=None):
        self.SIZE = size
        self.WIDTH, self.HEIGHT = size
        self.width, self.height = size

        if arrow_pos is not None:
            self.ARROW_X, self.ARROW_Y = arrow_pos

        if new_window:
            self.screen = pygame.display.set_mode(self.SIZE)
            pygame.display.set_caption(caption)
        else:
            self.screen = pygame.Surface(self.SIZE)

        self.background=background

    def blit(self, content, coords):
        self.screen.blit(content, coords)

    def refresh(self, back=False, scroll=0, show_mouse_pos=True):
        left_arrow = pygame.transform.scale(pygame.image.load(get_path('images/left-arrow.png')), (32, 32))
        arrow_rect = pygame.Rect(self.ARROW_X, self.ARROW_Y, 32, 32)

        if isinstance(self.background, tuple): # if the background is an image
            self.screen.fill(self.background)

        else:
            # print(self.background)
            for i in range(4):
                self.screen.blit(self.background,((i*self.SIZE[0]) + scroll,0))

        if back: self.screen.blit(left_arrow,(self.ARROW_X,self.ARROW_Y))
        if show_mouse_pos:
            mouse_pos = self.MEDIUM_FONT.render(str(pygame.mouse.get_pos()),1,self.WHITE)
            rect = mouse_pos.get_rect()
            self.screen.blit(mouse_pos,((self.WIDTH-rect.w)//2,0))

    def check_return(self, mouse_pos=None):
        if not mouse_pos:
            mouse_pos = pygame.mouse.get_pos()
        left_arrow = pygame.transform.scale(pygame.image.load(get_path('images/left-arrow.png')),(32,32))
        arrow_rect = pygame.Rect(self.ARROW_X,self.ARROW_Y,32,32)

        if arrow_rect.collidepoint(mouse_pos): return 1

    def draw_text(self,text,pos,size='MEDIUM',color=WHITE,center=False):
        text = eval(f'self.{size.upper()}_FONT.render(text, True, color)')
        rec=text.get_rect()
        x, y = pos
        if center:
            x = (self.WIDTH-rec.w)//2
        self.screen.blit(text,(x,y))


