import pygame,os
from WINDOW import Display
import WINDOW

pygame.init()
clock = pygame.time.Clock()

x,y = WINDOW.x,WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

window = Display()

class Player:
	def __init__(self,x,y,w,h):
		self.rect = pygame.Rect(x,y,w,h)
		self.x = x
		self.y = y
		self.x_vel = 2
		self.gravity = 9
		self.jump_lock = True

	def jump(self):
		if not self.jump_lock:
			print(self.gravity)
			self.gravity += 0.35
			self.gravity = min(9,self.gravity)


def draw_grid(scroll=0):
	tiles_x, tiles_y = window.TILE_DIMENSION_X,window.TILE_DIMENSION_Y
	lines_x = window.screen.get_width()//tiles_x
	lines_y = window.screen.get_height()//tiles_y

	#vertical lines
	for j in range(window.MAX_BLOCKS_X + 1):
		x=(j*tiles_x)
		pygame.draw.line(window.screen,(200,200,200),(x + scroll,0),(x + scroll,window.screen.get_height()))

	#horizontal liens
	for i in range(lines_y + 1):
		y = (i*tiles_y)
		pygame.draw.line(window.screen,(200,200,200),(0 + scroll,y),(window.WIDTH*4+scroll,y))

def main():
	player = Player(50,50,46,46*2)
	gravity = 9

	jump = False
	jump_lock = False

	while True:
		window.refresh()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and not(player.jump_lock):
					player.gravity *= -1
					player.jump_lock = False

		keys = pygame.key.get_pressed()
		if keys[pygame.K_d]:
			player.rect.x += player.x_vel

		pygame.draw.rect(window.screen,(255,0,0),(20,20,50,50))
		pygame.draw.rect(window.screen,(255,255,255),player.rect)

		if player.rect.y + player.rect.h + player.gravity < window.HEIGHT:
			player.rect.y += player.gravity
		else:
			player.rect.y = window.HEIGHT - player.rect.h
			player.jump_lock = False

		draw_grid()
		
		player.jump() # check player jumps
		
		pygame.display.update()
		clock.tick(60)

main()