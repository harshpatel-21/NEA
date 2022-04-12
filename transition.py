import pygame
from WINDOW import Display as window

class Transition:
    def __init__(self):
        time = 0.7*60
        self.x_vel = (window.WIDTH//2)//time
        self.y_vel = (window.HEIGHT//2)//time
        self.acceleration = 2
        self.faded_in = self.faded_out = False
        self.window = window

    def fade_in(self, surface):
        # print('here')
        if not self.faded_in:
            if self.rec_y1.bottom >= 0: self.rec_y1.y -= self.y_vel
            if self.rec_y2.top <= window.HEIGHT: self.rec_y2.y += self.y_vel

        if not(self.rec_y1.bottom >= 0 and self.rec_y2.top <= window.HEIGHT):
            self.faded_in = True
        # self.rec_y1.y -= self.y_vel
        # self.rec_y2.y += self.y_vel
        pygame.draw.rect(surface, (0,0,0), self.rec_y1)
        pygame.draw.rect(surface, (0,0,0), self.rec_y2)
        pass

    def fade_out(self, surface):
        if not self.faded_out:
            if self.rec_y1.bottom <= window.HEIGHT//2: self.rec_y1.y += self.y_vel
            if self.rec_y2.top >= window.HEIGHT//2: self.rec_y2.y -= self.y_vel

        if not(self.rec_y1.bottom <= window.HEIGHT // 2 <= self.rec_y2.top):
            self.faded_out = True

        pygame.draw.rect(surface, (0,0,0), self.rec_y1)
        pygame.draw.rect(surface, (0,0,0), self.rec_y2)
        pass

    def set_up(self, fade=1):
        self.faded_in = self.faded_out = False
        if fade ==-1:
            self.rec_y1 = pygame.Rect(0,-window.HEIGHT//2,window.WIDTH,window.HEIGHT//2)
            self.rec_y2 = pygame.Rect(0,window.HEIGHT,window.WIDTH,window.HEIGHT//2)

        if fade == 1:
            self.rec_y1 = pygame.Rect(0,0,window.WIDTH,window.HEIGHT//2)
            self.rec_y2 = pygame.Rect(0,window.HEIGHT//2,window.WIDTH,window.HEIGHT//2)