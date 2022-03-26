import pygame, sys
import os

# x='\\'.join(os.path.abspath(__file__).split('\\')[:-1]) # allow imports from main folder
# print(x)
# sys.path.insert(1,x)

from WINDOW import Display
current_path = os.path.dirname(__file__) # Where your .py file is located
image_path = os.path.join(current_path, 'images') # The image folder path

pygame.init()
class Item(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y, scale):
        super().__init__()
        self.item_type = item_type
        self.x,self.y = x,y
        self.animation = []
        self.get_animations()
        self.animation_pointer = 0
        self.image = self.animation[self.animation_pointer]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + Display.TILE_DIMENSION_X//2, y + (Display.TILE_DIMENSION_Y - self.image.get_height())) # make it so that its at the center of a tile, even if the size isn't the same
        self.initial_time = pygame.time.get_ticks()

    def draw(self,surface):
        surface.blit(self.image,self.rect.midtop)

    def animation_handling(self):
        cooldown_time = 60
        current_time = pygame.time.get_ticks()

        if current_time - self.initial_time >= cooldown_time:
            self.animation_pointer = (self.animation_pointer + 1)%len(self.animation)
            self.initial_time = current_time

        self.image = self.animation[self.animation_pointer]
        self.rect = self.image.get_rect()
        self.rect.midtop = (self.x + Display.TILE_DIMENSION_X//2, self.y + (Display.TILE_DIMENSION_Y - self.image.get_height())) # make it so that its at the center of a tile, even if the size isn't the same


    def get_animations(self):
        item_path = os.path.join(image_path,self.item_type)
        animation_scale = {'coin':(int(32*0.8),int(32*0.9))}
        images = os.listdir(f'images/{self.item_type}') # get a list of the image names for the animation
        for image in images:
            image = pygame.image.load(os.path.join(item_path,image))
            self.animation += [pygame.transform.scale(image,animation_scale.get(self.item_type))]
