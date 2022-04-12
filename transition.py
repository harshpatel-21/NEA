import pygame
from WINDOW import Display as window

class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction # 1 == fade outwards, -1 == fade inwards
        time = 0.9*60
        self.color = color
        # adjust the speed such that the vertical and horizontal walls reach the sides at the same time
        self.speed_x = (window.WIDTH//2)/time
        self.speed_y = (window.HEIGHT//2)/time
        self.fade_counter_x = self.fade_counter_y = 0

    def fade(self, surface):
        fade_complete = False
        self.fade_counter_x += self.speed_x
        self.fade_counter_y += self.speed_y
        counter_x = self.fade_counter_x * self.direction
        counter_y = self.fade_counter_y * self.direction
        # horizontal movement
        pygame.draw.rect(surface, self.color, (0 - counter_x, 0, window.WIDTH//2, window.HEIGHT))
        pygame.draw.rect(surface, self.color, (window.WIDTH//2 + counter_x, 0, window.WIDTH//2, window.HEIGHT))
        # vertical movement
        pygame.draw.rect(surface, self.color, (0, 0 - counter_y, window.WIDTH, window.HEIGHT//2))
        pygame.draw.rect(surface, self.color, (0, window.HEIGHT//2 + counter_y, window.WIDTH, window.HEIGHT//2))

        return fade_complete