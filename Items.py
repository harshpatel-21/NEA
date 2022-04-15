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


class AnimatedTile(pygame.sprite.Sprite):
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
        self.rect.midtop = (x + Display.TILE_DIMENSION_X // 2, y)  # make it so that its at the center of a tile, even if the size isn't the same
        self.initial_time = pygame.time.get_ticks()
        self.obj_type = item_type

    def draw(self, surface, target):
        temp = self.rect.copy()
        x, y = target.rect.topleft
        temp.x = temp.x - x + Display.WIDTH//2
        temp.y = temp.y - y + Display.HEIGHT//2
        # midtop = self.rect.midtop
        # self.rect.midtop = (midtop[0] - (Display.TILE_DIMENSION_X - self.rect.w)//2 - 2, midtop[1])
        pos = self.rect
        surface.blit(self.image, temp)

    def update(self, obj, camera):
        # do the animation handling
        self.animation_handling()
        # check for collision
        if not obj: return # if no object is passed then return
        # flips the mask of the image during collision detection
        obj_mask = pygame.mask.from_surface(pygame.transform.flip(obj.image, obj.direction==-1, False))
        offset_x = camera.rect.x - self.rect.x
        offset_y = camera.rect.y - self.rect.y
        collision = self.mask.overlap(obj_mask,(offset_x,offset_y))
        if collision:
            if self.obj_type == 'coin':
                print('coin collected!')
                self.kill() # remove the item from the group once its been interacted with
            return self
        return collision

    def animation_handling(self):
        cooldown_time = 60
        if self.obj_type == 'portal':
            cooldown_time = 100
        current_time = pygame.time.get_ticks()

        if current_time - self.initial_time >= cooldown_time:
            self.animation_pointer = (self.animation_pointer + 1) % len(self.animation)
            self.initial_time = current_time

        self.image = self.animation[self.animation_pointer]
        rec = self.rect
        # self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        tile_x, tile_y = Display.TILE_DIMENSION_X, Display.TILE_DIMENSION_Y

        # make it so that its at the center of a tile, even if the tile size isn't the same as item size
        # self.rect.midtop = (self.x + tile_x // 2, self.y + (tile_y - self.image.get_height()))
        # self.rect.topleft = rec.topleft

    def get_animations(self):
        item_path = os.path.join(image_path, self.item_type)
        animation_scale = {'coin': (int(32 * 0.8), int(32 * 0.9)),'portal':(92,92)}
        images = os.listdir(item_path)  # get a list of the image names for the animation
        for image in images:
            image = pygame.image.load(os.path.join(item_path, image))
            self.animation += [pygame.transform.scale(image, animation_scale.get(self.item_type)).convert_alpha()]

class Decoration(pygame.sprite.Sprite):
    def __init__(self, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect
        self.direction = 0
        self.obj_type = 'Decoration'
        # self.rect.midtop = (x + Display.TILE_DIMENSION_X // 2, y + (Display.TILE_DIMENSION_Y - self.rect.h))

    def draw(self, surface, scroll=0):
        self.rect.x += scroll
        # midtop = self.rect.midtop
        # self.rect.midtop = (midtop[0] - (Display.TILE_DIMENSION_X - self.rect.w)//2 - 2, midtop[1])
        # surface.blit(self.image, self.rect.midtop)
        surface.blit(self.image, self.rect)

class DeathBlock(pygame.sprite.Sprite):
    def __init__(self, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect
        self.direction = 0
        self.obj_type = 'Death Block'
        # self.rect.midtop = (x + (Display.TILE_DIMENSION_X//2), y + (Display.TILE_DIMENSION_Y - self.rect.h))

    def draw(self, surface, target):
        # self.rect.x += scroll
        # midtop = self.rect.midtop
        # self.rect.midtop = (midtop[0] - (Display.TILE_DIMENSION_X - self.rect.w)//2 - 2, midtop[1])
        # surface.blit(self.image, self.rect.midtop)
        temp = self.rect.copy()
        x, y = target.rect.topleft
        temp.x = temp.x - x + Display.WIDTH//2
        temp.y = temp.y - y + Display.HEIGHT//2
        surface.blit(self.image, temp)

    def collision(self, objs):
        if isinstance(objs, Group):
            for obj in objs:
                collision = self.mask_collision(obj)
                if collision:
                    obj.health = 0

        else:
            collision = self.mask_collision(objs) and objs.rect.y + objs.rect.h*0.5 >= self.rect.y # if more than half of body is submerged
            if collision:
                objs.health = 0

    def update(self, objs):
        self.collision(objs)

    def mask_collision(self, obj):
        mask = pygame.mask.from_surface(self.image)
        offset = (obj.rect.x - self.rect.x, obj.rect.y - self.rect.y)
        return mask.overlap(obj.mask,offset)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 0
        self.obj_type = 'Obstacle'

    def draw(self, surface, scroll, player=None):
        self.rect.x += scroll
        surface.blit(self.image, self.rect)

    def mask_collision(self, rect, mask):
        x = rect.x - self.rect.x
        y = rect.y - self.rect.y
        return self.mask.overlap(mask, (x,y))