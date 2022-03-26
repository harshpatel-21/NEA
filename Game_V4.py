import os,sys
# v3:
# - made it so that the player cannot hit with a sword whilst in bow animation and making sure the player is alive
# - fixed an error where player could move whilst in a action animation which would crash the player
#   animations.

#v4:
# - when player was in attack animation in direction x and held movement key in opposing direction, once the
#   animation finished, it wouldn't do so. To fix fix this, added pygame.key.get_pressed()
#   so that once animation is finished and another direction key is held during animation, it wil
#   to move player in that direction. Makes it more fluid.
# - whilst in an animation, if the player changed direction before/at the point when arrow is shot
#   it would change the direction of the player but unintentinally change the arrow's direction as well.
#   fixed this by making it so that the player cannot change direction during the attack animations.

# insert at 1, 0 is the script path (or '' in REPL)

x='\\'.join(os.path.abspath(__file__).split('\\')[:-2]) # allow imports from main folder
print(x)
sys.path.insert(1,x)

# EDIT FOR IMAGES: DIMENSIONS SHOULD BE 17x30
from entity_class import Entity,Arrow
import WINDOW
import pygame, re, json, WINDOW, math
from boxes import Textbox, Inputbox
from Items import Item

pygame.init()

x,y = WINDOW.x,WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

current_path = os.path.dirname(__file__) # Where your .py file is located
image_path = os.path.join(current_path, 'images') # The image folder path
coin_path = os.path.join(image_path,'coin')

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)
LEVEL = 1
# background = pygame.transform.scale(pygame.image.load(WINDOW.get_path('backgrounds/background_1.png')),window.SIZE)
# window.background = background

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

scale = (55,92) # for normal
# scale = (60,92) # with sword

def main(LEVEL):
	scale = (55,92) # for normal
	# scale = (60,92) # with sword
	player = Player(100,100,'player',scale)
	# enemy = Player(500,100,'enemy',scale,all_animations = ['Idle','Die'],max_health = 50 )
	player2 = Player(500,100,'player2',(int(70 * 2.4), 92),all_animations = ['Idle','Die'],max_health = 50 )
	pygame.image.load(os.path.join(coin_path, '1.png'))

	coin = Item('coin',50,50,(32,32))
	# player = player_right[0]
	moving_right = moving_left = False
	arrows = []
	bow_finished = False

	#sprite groups
	arrows = []
	enemies = [player2]

	player2.direction = -1
	player.weapon = 1
	while True:
		coin.animation_handling()
		action_conditions = not player.in_air and player.health # making sure player isn't in the air and is still alive
		attack_conditions = not(player.sword_attack or player.bow_attack) # only allow attacking if not already in attack animation -> ADD INTO ITERATIVE DEVELOPMENT
		window.refresh()
		player.check_alive()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

			# check for keyboard input
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return()
				if event.key == pygame.K_r:
					for enemy in enemies:
						enemy.health = enemy.max_health
						enemy.update_action(0)

				# jumping
				if event.key == pygame.K_w and action_conditions and attack_conditions:
					player.jumping = True
					player.in_air = True

				# attacking
				if event.key == pygame.K_SPACE and action_conditions and attack_conditions:
					if player.current_weapon == 1: # sword selected
						player.sword_attack = True
					elif player.current_weapon == 2 and player.shoot_cooldown_timer == 0: # bow selected
						player.bow_attack = True
						player.shoot_cooldown_timer = player.shoot_cooldown

				# weapon selection
				if event.key == pygame.K_1:
					player.current_weapon = 1
				if event.key == pygame.K_2:
					player.current_weapon = 2

			# check for keys that are lifted/ no longer being pressed
			if event.type == pygame.KEYUP:
				# # player movement
				# if event.key == pygame.K_a:
				# 	moving_left = False
				# if event.key == pygame.K_d:
				# 	moving_right = False
				pass

		keys = pygame.key.get_pressed()
		moving_left = keys[pygame.K_a] and attack_conditions
		moving_right = keys[pygame.K_d] and attack_conditions


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
				player.update_action(0) # set back to idle animation if no other action is being performed


		add_arrow = player.animation_handling()
		if add_arrow:
			arrows += [add_arrow]

		for arrow in arrows:
			arrow.draw(window.screen)
			# if pygame.sprite.spritecollide(arrow,enemies,True,pygame.sprite.collide_mask):
			# 	arrow.remove = True
			for enemy in enemies:
				if not enemy.check_alive():
					continue
				if arrow.check_collision(enemy):
					arrow.remove = True
					arrow.kill()
					enemy.health -= player.current_weapon_damage.get(player.current_weapon) # do damange based on current weapon
					print(enemy.health)
					break # no need to check collision with other enemies if already collided
			else:
				arrow.update()

			if arrow.remove:
				arrow.kill() # free up memory by removing this arrow instance
				arrows.remove(arrow) # remove the arrow instance from memory

		# enemies.draw(window.screen)

		# draw_map(map_array)
		pygame.draw.line(window.screen,(255,0,0),(0,300),(window.WIDTH,300))

		# enemy handling
		for enemy in enemies: # if enemy has died
			enemy.check_collision(player) # check for player collision (mainly whilst in sword animation)
			if enemy.health <= 0:
				# enemies.remove(enemy) # remove from array -> change this to death animation afterwards
				# enemy.kill()
				# enemy.update_action(number which points to death animation)
				pass
			else:
				enemy.check_collision(player)
				enemy.move(False,False) # move enemy if need be
			enemy.draw(window.screen)
			enemy.animation_handling()


				# if enemy.check_collision(player): # if enemy is alive and their sprite has collided with player
				# 	# print(enemy.health)
				# 	# enemy.health -= 50
				# 	pass

		player.draw(window.screen)
		player.move(moving_left, moving_right)

		window.draw_text(f'weapon: {["Sword","Bow"][player.current_weapon==2]}',(10,7))
		window.draw_text(f'Press [1] to use Sword, [2] to use Bow',(10,20))
		coin.draw(window.screen)

		pygame.display.update()

		clock.tick(FPS)
if __name__ == "__main__":
	main(LEVEL)
