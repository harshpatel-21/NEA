import pygame
from WINDOW import Display as window

class ScreenFade:
    def __init__(self, direction, color, time):
        self.direction = direction # 1 == fade outwards, -1 == fade inwards
        time = time*60 # 60 is the FPS
        self.color = color
        # adjust the speed such that the vertical and horizontal walls reach the sides at the same time
        self.speed_x = (window.WIDTH//2)/time
        self.speed_y = (window.HEIGHT//2)/time
        self.fade_counter_x = self.fade_counter_y = 0
        self.acceleration = 2

    def fade(self, surface):
        fade_complete = False
        self.fade_counter_x += self.speed_x * self.acceleration
        self.fade_counter_y += self.speed_y * self.acceleration
        self.acceleration *= 0.96
        counter_x = self.fade_counter_x
        counter_y = self.fade_counter_y
        if self.direction == 1:
            # horizontal movement
            pygame.draw.rect(surface, self.color, (0 - counter_x, 0, window.WIDTH//2, window.HEIGHT))
            pygame.draw.rect(surface, self.color, (window.WIDTH//2 + counter_x, 0, window.WIDTH//2, window.HEIGHT))
            # vertical movement
            pygame.draw.rect(surface, self.color, (0, 0 - counter_y, window.WIDTH, window.HEIGHT//2))
            pygame.draw.rect(surface, self.color, (0, window.HEIGHT//2 + counter_y, window.WIDTH, window.HEIGHT//2))

            # if counter_x > window.WIDTH//2 and counter_y > window.HEIGHT//2:
            #     fade_complete = True
        else:
            pygame.draw.rect(surface, self.color, (-window.WIDTH//2 + counter_x, 0, window.WIDTH//2, window.HEIGHT))
            pygame.draw.rect(surface, self.color, (window.WIDTH - counter_x, 0, window.WIDTH//2, window.HEIGHT))
            pygame.draw.rect(surface, self.color, (0, -window.HEIGHT//2 + counter_y, window.WIDTH, window.HEIGHT//2))
            pygame.draw.rect(surface, self.color, (0,window.HEIGHT - counter_y, window.WIDTH, window.HEIGHT//2))
        if counter_x - 2 > window.WIDTH//2 and counter_y - 2 > window.HEIGHT//2:
            fade_complete = True
            self.acceleration = 2
            self.fade_counter_x = 0
            self.fade_counter_y = 0
        return fade_complete