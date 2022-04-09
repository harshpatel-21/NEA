import os, sys, csv, json
from WINDOW import get_path
from openpyxl import load_workbook
from boxes import Textbox
# from entity_class import Entity, Enemy, Projectile, Player, Group
import pygame, WINDOW
# from Items import Item, Decoration, DeathBlock
# from level_editor import load_level, draw_grid
#
# pygame.init()
#
# x, y = WINDOW.x, WINDOW.y
# os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
#
# current_path = os.path.dirname(__file__)  # Where your .py file is located
# image_path = os.path.join(current_path, 'images')  # The image folder path
# coin_path = os.path.join(image_path, 'coin')
#
# FPS = 60
# clock = pygame.time.Clock()
# window = WINDOW.Display(new_window=True)
# LEVEL = 2
# TILE_TYPES = os.listdir(f'images/tiles/{2}')
# img_list = []
# TILE_SCALE = (window.TILE_DIMENSION_X, window.TILE_DIMENSION_Y)
# tile_x,tile_y = TILE_SCALE
# # flip_images = [15]
# # entities = [17, 18]
# img_list = {}
# for i in TILE_TYPES:
#     img = pygame.transform.scale(pygame.image.load(WINDOW.get_path(f'images/tiles/{LEVEL}/{i}')).convert_alpha(), TILE_SCALE)
#     # if i in flip_images: img = pygame.transform.flip(img, False, True)
#     # if i in entities: img = pygame.transform.scale(img, (46,92))
#     name = i[:i.index('.')]
#     img_list[name] = img
#
# print(img_list)
#
# class Tile:
#     def __init__(self, image, rect):
#         self.image = image
#         self.rect = rect
#         self.mask = pygame.mask.from_surface(self.image)
#
#     def draw(self):
#         window.screen.blit(self.image, self.rect)
#
# def load_level(level):
#     layers = {}
#     path = f'levels/level{level}'
#     files = os.listdir(path)
#     ordered = sorted(files, key = lambda i: int(i.split('_')[1][:i.split('_')[1].index('.')])) # sort based on layer
#     # print(ordered)
#
#     for index, file in enumerate(files):
#         with open(os.path.join(path, file)) as file:
#             level = csv.reader(file, delimiter=',')
#             x = []
#             # for row in level:
#             #     x+=[[*map(int,row)]]
#             layers[index] = [*level]
#         # sys.exit()
#     return layers
#
# game_level = load_level(2)
# print(game_level)
#
# def process_data(data):
#     obstacles = []
#     # obstacles.append()
#     for layer in data.values():
#         for y, row in enumerate(layer):
#             for x, tile in enumerate(row):
#                 if tile == '-1':
#                     continue
#                 tile = Tile(img_list[tile], (tile_x * x, tile_y*y, tile_x, tile_y))
#                 obstacles += [tile]
#     return obstacles
# level = process_data(game_level)
#
# # while 1:
# #     window.refresh()
# #     for event in pygame.event.get():
# #         if event.type == pygame.QUIT:
# #             pygame.quit()
# #             sys.exit()
# #     for tile in level:
# #         window.screen.blit(tile.image,tile.rect)
# #     pygame.display.update()
# #     clock.tick(FPS)
# ---------------------------- Loading and storing Excel stuff -----------------------------
# book = load_workbook('questions.xlsx')
# current_sheet = book['1.1']
# questions = {
#     1:{
#         'right':1,
#         'wrong':3
#     }
# }
# id = 1
# print(current_sheet['A'])
# for question, row in enumerate(current_sheet):
#     print(row)
#     for index, cell in enumerate(row):
#         # changing values after questions completed:
#
#         if not current_sheet[f'A{question+1}'].value in questions:
#             continue
#         # print(cell.value)
#         right_ind = 5+(id*2)
#         wrong_ind = right_ind + 1
#         if index == right_ind:
#             cell.value = questions[question+1]['right']
#         elif index == wrong_ind:
#             cell.value = questions[question+1]['wrong']
#
#         pass
#
# book.save('Questions/questions.xlsx')
# print(questions)

# --------------------------- text boxes -----------------------------------
pygame.init()

x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True,caption='Question Display')

class QuestionBox(Textbox):
    LARGE_FONT = pygame.font.SysFont('Sans', 35)
    MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)
    MEDIUM_FONT = pygame.font.SysFont('Sans', 25)
    SMALL_FONT = pygame.font.SysFont('Sans', 15)
    def __init__(self, x, y, size):
        # inherit a few methods
        super().__init__(x, y)
        # self.check_hover = Textbox.check_hover
        # self.check_click = Textbox.check_click
        self.x,self.y = x,y
        self.rect = pygame.Rect(x,y,*size)
        self.surface = pygame.Surface(self.rect.size)
        self.background = (0,0,0)
        text_rect_size = [*map(lambda i: i*0.8,self.rect.size)] # create a padding
        dx = text_rect_size[0]
        self.text_rect = pygame.Rect((self.rect + ()))

    def show(self, surface):
        self.surface.fill((0,0,0))
        pygame.draw.rect(self.surface, self.background, (0, 0, self.rect.w, self.rect.h))
        surface.blit(self.surface,(self.x,self.y))

    def add_text(self, text):
        pass

center = [*window.screen.get_rect().center]
a = QuestionBox(center[0]-50,center[1]-50,(100,100))

text = 'Hello'
while 1:
    window.refresh()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(a.check_click(pygame.mouse.get_pos())) # only check for click collision if need be

    a.check_hover()
    a.show(window.screen)

    pygame.display.update()
    clock.tick(FPS)
