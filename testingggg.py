# import os, sys, csv
# from entity_class import Entity, Enemy, Projectile, Player, Group
# import pygame, WINDOW
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
for i in range(1,3):
    with open(f'Questions/2.{i}.xlsx','w+') as file:
        pass