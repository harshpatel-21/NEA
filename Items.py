import pygame, sys
import os

# x='\\'.join(os.path.abspath(__file__).split('\\')[:-1]) # allow imports from main folder
# print(x)
# sys.path.insert(1,x)

from WINDOW import Display
from entity_class import Group

current_path = os.path.dirname(__file__)  # Where your .py file is located
image_path = os.path.join(current_path, 'images', 'items') # The image folder path
# print(image_path)
pygame.init()


class Item(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.x, self.y = x, y
        self.animation = []
        self.get_animations()
        self.animation_pointer = 0
        self.image = self.animation[self.animation_pointer]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + Display.TILE_DIMENSION_X // 2, y + (
                Display.TILE_DIMENSION_Y - self.image.get_height()))  # make it so that its at the center of a tile, even if the size isn't the same
        self.initial_time = pygame.time.get_ticks()

    def draw(self, surface, scroll=0):
        self.rect.x += scroll
        # midtop = self.rect.midtop
        # self.rect.midtop = (midtop[0] - (Display.TILE_DIMENSION_X - self.rect.w)//2 - 2, midtop[1])
        pos = self.rect
        surface.blit(self.image, pos)

    def update(self, obj=None):
        # do the animation handling
        self.animation_handling()
        # check for collision
        if not obj: return # if no object is passed then return
        # flips the mask of the image during collision detection
        obj_mask = pygame.mask.from_surface(pygame.transform.flip(obj.image, obj.direction==-1, False))
        offset_x = obj.rect.x - self.rect.x
        offset_y = obj.rect.y - self.rect.y
        collision = self.mask.overlap(obj_mask,(offset_x,offset_y))
        if collision:
            if self.item_type == 'coin':
                print('coin collected!')
            self.kill() # remove the item from the group once its been interacted with

    def animation_handling(self):
        cooldown_time = 60
        current_time = pygame.time.get_ticks()

        if current_time - self.initial_time >= cooldown_time:
            self.animation_pointer = (self.animation_pointer + 1) % len(self.animation)
            self.initial_time = current_time

        self.image = self.animation[self.animation_pointer]
        rec = self.rect
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        tile_x, tile_y = Display.TILE_DIMENSION_X, Display.TILE_DIMENSION_Y

        # make it so that its at the center of a tile, even if the tile size isn't the same as item size
        # self.rect.midtop = (self.x + tile_x // 2, self.y + (tile_y - self.image.get_height()))
        self.rect.topleft = rec.topleft

    def get_animations(self):
        item_path = os.path.join(image_path, self.item_type)
        animation_scale = {'coin': (int(32 * 0.8), int(32 * 0.9))}
        images = os.listdir(item_path)  # get a list of the image names for the animation
        for image in images:
            image = pygame.image.load(os.path.join(item_path, image))
            self.animation += [pygame.transform.scale(image, animation_scale.get(self.item_type)).convert_alpha()]

class Decoration(pygame.sprite.Sprite):
    def __init__(self, value, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.value = value
        self.image = image
        self.rect = rect
        # self.rect.midtop = (x + Display.TILE_DIMENSION_X // 2, y + (Display.TILE_DIMENSION_Y - self.rect.h))

    def draw(self, surface, scroll=0):
        self.rect.x += scroll
        # midtop = self.rect.midtop
        # self.rect.midtop = (midtop[0] - (Display.TILE_DIMENSION_X - self.rect.w)//2 - 2, midtop[1])
        # surface.blit(self.image, self.rect.midtop)
        surface.blit(self.image, self.rect)

class DeathBlock(pygame.sprite.Sprite):
    def __init__(self, value, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.value = value
        self.image = image
        self.rect = rect
        # self.rect.midtop = (x + (Display.TILE_DIMENSION_X//2), y + (Display.TILE_DIMENSION_Y - self.rect.h))

    def draw(self, surface, scroll=0):
        self.rect.x += scroll
        # midtop = self.rect.midtop
        # self.rect.midtop = (midtop[0] - (Display.TILE_DIMENSION_X - self.rect.w)//2 - 2, midtop[1])
        # surface.blit(self.image, self.rect.midtop)
        surface.blit(self.image, self.rect)

    def collision(self, objs):
        if isinstance(objs, Group):
            for obj in objs:
                collision = self.mask_collision(obj)
                if collision:
                    obj.health = 0
        else:
            collision = self.mask_collision(objs)
            if collision: objs.health = 0

    def update(self, objs):
        self.collision(objs)

    def mask_collision(self, obj):
        mask = pygame.mask.from_surface(self.image)
        offset = (obj.rect.x - self.rect.x, obj.rect.y - self.rect.y)
        return mask.overlap(obj.mask,offset)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, value, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.value = value
        self.image = image
        self.rect = rect
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface, scroll):
        self.rect.x += scroll
        surface.blit(self.image, self.rect)