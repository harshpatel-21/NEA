import pygame
from WINDOW import Display as window

class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction # 1 == fade outwards, -1 == fade inwards
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self, surface):
        fade_complete = False
        self.fade_counter += self.speed
        counter = self.fade_counter * self.direction
        # horizontal movement
        pygame.draw.rect(surface, self.color, (0 - counter, 0, window.WIDTH//2, window.HEIGHT))
        pygame.draw.rect(surface, self.color, (window.WIDTH//2 + counter, 0, window.WIDTH//2, window.HEIGHT))
        # vertical movement
        pygame.draw.rect(surface, self.color, (0, 0 - counter, window.WIDTH, window.HEIGHT//2))
        pygame.draw.rect(surface, self.color, (0, window.HEIGHT//2 + counter, window.WIDTH, window.HEIGHT//2))

        return fade_complete