import os,sys

# - made it so that the player cannot hit with a sword whilst in bow animation and making sure the player is alive
# - fixed an error where player could move whilst in a action animation which would crash the player
#   animations.

# insert at 1, 0 is the script path (or '' in REPL)

x='\\'.join(os.path.abspath(__file__).split('\\')[:-2]) # allow imports from main folder
print(x)
sys.path.insert(1,x)

# EDIT FOR IMAGES: DIMENSIONS SHOULD BE 17x30

import pygame, re, json, WINDOW, math
from WINDOW import Display
from boxes import Textbox, Inputbox
from level_editor import load_level
from entity_class import Entity
from level_editor import load_level

pygame.init()

FPS = 60
clock = pygame.time.Clock()
window = Display(new_window=True)
LEVEL = 1
# background = pygame.transform.scale(pygame.image.load(WINDOW.get_path('backgrounds/background_1.png')),window.SIZE)
# window.background = background
map_array = load_level(2)
def draw_map(arr):
	for y,row  in enumerate(arr):
		for x,tile in enumerate(row):
			if tile not in [-1,16]:
				img = pygame.transform.scale(pygame.image.load(f'images/tiles/{LEVEL}/{tile+1}.png'),(46,46))
				window.screen.blit(img,(x*46,y*46))
# player_right = []
# player_left = []

# for j in range(1,4):
# 	img = pygame.image.load(f'images/char_idle/idle_{j}.png')
# 	img = pygame.transform.scale(img,(46,92))
# 	player_right += [img]
# 	player_left += [pygame.transform.flip(img,True,False)]


GRAVITY = 0.75
class Player(Entity):
	def __init__(self,*args,**kwargs):
		Entity.__init__(self,*args,**kwargs)

class Arrow(pygame.sprite.Sprite):
	def __init__(self, shooter):
		self.img = pygame.image.load('images/Arrow04.png')
		self.rect = self.img.get_rect()
		self.rect.topleft = (shooter.rect.x,shooter.rect.y)
		self.direction = shooter.direction

		if self.direction == 1: # adjusting starting position of arrow
			self.rect.x += shooter.rect.w
		else:
			self.rect.x -= self.rect.w

		self.rect.y = shooter.rect.y+32
		self.x_vel = 20
		self.acceleration = 3
		self.initial_time = pygame.time.get_ticks()
		degrees = 2
		self.theta = math.pi*degrees/180
		self.initial_y = self.rect.y
		self.initial_x = self.rect.x
		self.initial_rect = self.rect.copy()
		self.img_copy = self.img.copy()
		self.angle = degrees

	def show(self, surface):
		surface.blit(pygame.transform.flip(self.img, self.direction==-1, False), self.rect)

	def move(self):
		self.rect.x += (self.x_vel*self.acceleration) * self.direction
		# self.acceleration -= 0.035*self.acceleration
		self.acceleration *= 0.9
		# time_passed = (pygame.time.get_ticks() - self.initial_time)/60
		#
		# ux = self.x_vel*math.cos(self.theta)
		# uy = self.x_vel*math.sin(self.theta)
		# old =
		# sx = (ux * time_passed)*self.acceleration*self.direction
		# sy = uy*time_passed + (GRAVITY/2*(time_passed**2))/2
		# dy =  self.initial_y + sy
		# ux = (ux*self.acceleration)*time_passed*self.direction
		# dx = self.initial_x + sx #(ux*self.acceleration)*time_passed*self.direction
		# self.acceleration = 0.98*self.acceleration
		# print(dx)
		# vy = uy + GRAVITY*time_passed
		# # angle = (180/math.atan(vy/ux))
		# # print(thing)
		# self.img_copy = pygame.transform.rotate(self.img,-self.angle)
		# # self.acceleration = max(1,self.acceleration)
		# self.rect.x = dx
		# self.rect.y = dy
		# self.angle -= -0.5



		# sy = usin(theta)*t + 1/2(GRAVITY)*t**2
		# sx = ucos(theta)*t



scale = (55,92) # for normal
# scale = (60,92) # with sword
player = Player(100,100,'player',scale)

def main(LEVEL):
	# player = player_right[0]
	moving_right = moving_left = False
	arrows = []
	bow_finished = False

	while True:
		action_conditions = not player.in_air and player.health # making sure player isn't in the air and is still alive
		attack_conditions = not(player.sword_attack or player.bow_attack) # only allow attacking if not already in attack animation -> ADD INTO ITERATIVE DEVELOPMENT
		window.refresh()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

			# check for keyboard input
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return()

				# player movement
				if event.key == pygame.K_a:
					moving_left = True
				if event.key == pygame.K_d:
					moving_right = True
				if event.key == pygame.K_w and action_conditions and attack_conditions:
					player.jumping = True
					player.in_air = True

				# attacking
				if event.key == pygame.K_SPACE and action_conditions and attack_conditions:
					if player.current_weapon == 1: # sword selected
						player.sword_attack = True
					elif player.current_weapon == 2: # bow selected
						player.bow_attack = True
				# weapon selection
				if event.key == pygame.K_1:
					player.current_weapon = 1
				if event.key == pygame.K_2:
					player.current_weapon = 2

			# check for keys that are lifted/ no longer being pressed
			if event.type == pygame.KEYUP:
				# player movement
				if event.key == pygame.K_a:
					moving_left = False
				if event.key == pygame.K_d:
					moving_right = False


		# update player animations
		if player.health: # if the player is alive
			if player.in_air: # if jumping
				if player.y_vel < 0: # if going upwards
					player.update_action(2)
					pass
				else: # if falling
					player.update_action(3)
					pass
			elif player.sword_attack: # if player is attacking with sword
				player.update_action(4)
			elif player.bow_attack: # if player is attacking with a bow
				bow_finished = player.update_action(5)
			elif moving_right or moving_left:
				player.update_action(1) # set the animation to run
			else:
				player.update_action(0) # set back to idle animation

		else:
			player.update_action(4) # death animation

		if bow_finished:
			arrows += [Arrow(player)]

		for arrow in arrows:
			arrow.show(window.screen)
			arrow.move()

		# draw_map(map_array)
		pygame.draw.line(window.screen,(255,0,0),(0,300),(window.WIDTH,300))
		bow_finished = player.animation_handling()
		player.draw(window.screen)
		player.move(moving_left, moving_right)
		pygame.display.update()

		clock.tick(FPS)
if __name__ == "__main__":
	main(LEVEL)
