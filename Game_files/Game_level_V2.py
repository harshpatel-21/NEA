import os,sys

# EDIT FOR IMAGES: DIMENSIONS SHOULD BE 17x30
x='\\'.join(os.path.abspath(__file__).split('\\')[:-2])
print(x)
sys.path.insert(1,x)

import pygame, re, json, WINDOW
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



class Player(Entity):
	def __init__(self,*args,**kwargs):
		Entity.__init__(self,*args,**kwargs)

scale = (55,92) # for normal
# scale = (60,92) # with sword
player = Player(100,100,'player',scale)

def main(LEVEL):
	# player = player_right[0]
	moving_right = moving_left = False
	while True:
		# action_conditions = not player.in_air and player.health
		action_conditions = True
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
				if event.key == pygame.K_w:
					player.jumping = True
					player.in_air = True
				if event.key == pygame.K_SPACE:
					player.sword_attack = True
				if event.key == pygame.K_r:
					player.bow_attack = True


			# check for keys that are lifted/ no longer being pressed
			if event.type == pygame.KEYUP:

				# player movement
				if event.key == pygame.K_a:
					moving_left = False
				if event.key == pygame.K_d:
					moving_right = False

		if player.health: # if the player is alive
			if player.in_air: # if jumping
				if player.y_vel < 0: # if going upwards
					player.update_action(2)
					pass
				else: # if falling
					player.update_action(3)
					pass
			elif player.sword_attack:
				player.update_action(4)
			elif player.bow_attack:
				player.update_action(5)
			elif moving_right or moving_left:
				player.update_action(1) # set the animation to run
			else:
				player.update_action(0) # set back to idle animation

		else:
			player.update_action(4) # death animation

		# draw_map(map_array)
		pygame.draw.line(window.screen,(255,0,0),(0,600),(window.WIDTH,600))
		player.animation_handling()
		player.draw(window.screen)
		player.move(moving_left, moving_right)
		pygame.display.update()

		clock.tick(FPS)

main(LEVEL)
