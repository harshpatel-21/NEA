import os, sys

# v3:
# - made it so that the player cannot hit with a sword whilst in bow animation and making sure the player is alive
# - fixed an error where player could move whilst in a action animation which would crash the player
#   animations.

# v4:
# - when player was in attack animation in direction x and held movement key in opposing direction, once the
#   animation finished, it wouldn't do so. To fix fix this, added pygame.key.get_pressed()
#   so that once animation is finished and another direction key is held during animation, it wil
#   to move player in that direction. Makes it more fluid.

# - whilst in an animation, if the player changed direction before/at the point when arrow is shot
#   it would change the direction of the player but unintentionally change the arrow's direction as well.
#   fixed this by making it so that the player cannot change direction during the attack animations.

# in entity_class, in the collision check for the Entity, added a 'self.collisions' counter to check if collisions
# occurred. Because if normal collision check was done, every collision check during combat animation, it would count
# overlap between the images as an attack and subtract the enemy health. Therefore, to prevent this, a counter was added
# to simply check if any collisions occurred between the two images during the combat animation, and if that counter is
# bigger than 0, it means combat collision occurred and so only the amount intended to be subtracted from the enemy is
# subtracted.
# ie dps = 20 for sword.
# before: each collision in the animation of a sword swing: damage == x * dps where x = number of frame collisions
# after: once sword animation ended, if there was contact at any frame which incremented the counter:  damage = dps

# insert at 1, 0 is the script path (or '' in REPL)

x = '\\'.join(os.path.abspath(__file__).split('\\')[:-2])  # allow imports from main folder
print(x)
sys.path.insert(1, x)

# EDIT FOR IMAGES: DIMENSIONS SHOULD BE 17x30
# if __name__ == 'Game_V4':
from entity_class import Entity, Enemy, Projectile, Player, Group
import pygame, WINDOW
from Items import Item, Decoration, Water
from level_editor import load_level, draw_grid

pygame.init()

x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

current_path = os.path.dirname(__file__)  # Where your .py file is located
image_path = os.path.join(current_path, 'images')  # The image folder path
coin_path = os.path.join(image_path, 'coin')

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)
LEVEL = 1
TILE_TYPES = len(os.listdir(f'images/tiles/{1}'))
img_list = []
TILE_SCALE = (window.TILE_DIMENSION_X, window.TILE_DIMENSION_Y)
for i in range(TILE_TYPES):
    img = pygame.transform.scale(pygame.image.load(WINDOW.get_path(f'images/tiles/{LEVEL}/{i}.png')).convert_alpha(), TILE_SCALE)
    if i in [11, 15]: img = pygame.transform.flip(img, False, True)
    if i in [16]: img = pygame.transform.scale(img, (46,92))
    img_list += [img]

background = pygame.transform.scale(pygame.image.load(WINDOW.get_path('backgrounds/background_1.png')),window.SIZE)
# window.background = background

# player_right = []
# player_left = []

# for j in range(1,4):
# 	img = pygame.image.load(f'images/char_idle/idle_{j}.png')
# 	img = pygame.transform.scale(img,(46,92))
# 	player_right += [img]
# 	player_left += [pygame.transform.flip(img,True,False)]


GRAVITY = 0.75

scale = (55, 92)  # for normal
# scale = (60,92) # with sword
# load in game data
class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # iterate through each value in level data file
        decorations = []
        waters = []
        enemies = []
        coins = []
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile == -1:
                    continue
                img = img_list[tile] # get the image from the list of images
                img_rect = img.get_rect()
                img_rect.topleft = (x * window.TILE_DIMENSION_X, y * window.TILE_DIMENSION_Y)
                img_mask = pygame.mask.from_surface(img)
                tile_data = (img, img_rect, img_mask)
                if 0 <= tile <= 10:
                    self.obstacle_list.append(tile_data)
                elif 11 <= tile <= 13: # grass / no collision decoration
                    decorations.append(Decoration(img, img_rect.x, img_rect.y))
                elif 13 <= tile <= 15: #water
                    waters.append(Water(img, img_rect.x, img_rect.y))
                elif tile == 16: # coin
                    coins += [Item('coin', img_rect.x, img_rect.y, (32, 32))]
                elif tile == 17: #create player
                    player = Player(img_rect.x, img_rect.y, 'player', scale, sword_dps=15)
        return player, decorations, waters, enemies, coins

    def draw(self, background, scroll=0):
        background_width = background.get_width()
        for i in range(4):
            window.screen.blit(background,((i * background_width) + scroll,0))

        for tile in self.obstacle_list:
            tile[1].x += scroll
            window.screen.blit(tile[0], tile[1])

game_level = load_level(1)
print(game_level)
world = World()

def main(level):
    # scale = (60,92) # with sword
    # player = Player(100, 100, 'player', scale, sword_dps=15)
    # enemy = Player(500,100,'enemy',scale,all_animations = ['Idle','Die'],max_health = 50 )
    player, decorations, waters, enemies, coins = world.process_data(game_level)
    enemy_1 = Enemy(500, 0, 'player2', (int(70 * 2.4), 92), all_animations=['Idle', 'Die', 'Run', 'Attack'],
                    max_health=100, x_vel=2)
    enemy_2 = Enemy(700, 0, 'player2', (int(70 * 2.4), 92), all_animations=['Idle', 'Die', 'Run', 'Attack'],
                    max_health=100, x_vel=2)
    enemy_3 = Enemy(400, 0, 'player2', (int(70 * 2.4), 92), all_animations=['Idle', 'Die', 'Run', 'Attack'],
                    max_health=100, x_vel=2)

    player.current_weapon_damage = {1: 50, 2: 50}
    # enemy_group.add(enemy_1,enemy_2)

    # sprite groups
    decoration_group = Group(*decorations)
    waters_group = Group(*waters)
    enemy_group = Group(enemy_1, enemy_2)
    arrow_group = Group()
    coin_group = Group(*coins)
    arrows = []
    # enemies = [enemy_1, enemy_2]
    # coin_group = pygame.sprite.Group()

    enemy_1.direction = -1
    player.weapon = 1

    screen_scroll = 0
    while True:
        action_conditions = not player.in_air and player.health  # making sure player isn't in the air and is still alive
        attack_conditions = not (
                player.sword_attack or player.bow_attack)  # only allow attacking if not already in attack animation -> ADD INTO ITERATIVE DEVELOPMENT
        window.refresh()
        world.draw(background, screen_scroll)
        # draw_grid(0)

        player.check_alive()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # check for keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ()

                if event.key == pygame.K_r:
                    enemy_group.regen()

                if event.key == pygame.K_h:
                    player.health += 50

                # jumping
                if event.key == pygame.K_w and action_conditions and attack_conditions:
                    player.jumping = True
                    # player.in_air = True

                # attacking
                if (event.key == pygame.K_SPACE) and action_conditions and attack_conditions:
                    if player.current_weapon == 1:  # sword selected
                        player.sword_attack = True
                    elif player.current_weapon == 2 and player.shoot_cooldown_timer == 0:  # bow selected
                        player.bow_attack = True
                        player.shoot_cooldown_timer = player.shoot_cooldown

                # weapon selection
                value = chr(event.key)
                if value in ['1', '2']:
                    player.current_weapon = int(value)

            # check for keys that are lifted/ no longer being pressed
            if event.type == pygame.KEYUP:
                # if event.key == pygame.K_a:
                #     moving_left = False
                # if event.key == pygame.K_d:
                #     moving_right = False
                pass

        keys = pygame.key.get_pressed()

        moving_left = keys[pygame.K_a] and attack_conditions
        moving_right = keys[pygame.K_d] and attack_conditions

        # update player animations
        if player.health:  # if the player is alive
            if player.in_air:  # if jumping
                if player.y_vel < 0:  # if going upwards
                    player.update_action(2)
                    pass
                else:  # if falling
                    player.update_action(3)
                    pass
            elif player.sword_attack:  # if player is attacking with sword
                player.update_action(4)
            elif player.bow_attack:  # if player is attacking with a bow
                player.update_action(5)
            elif moving_right or moving_left:
                player.update_action(1)  # set the animation to run
            else:
                player.update_action(0)  # set back to idle animation if no other action is being performed

        # creating an arrow instance if bow animation was activated
        add_arrow = player.animation_handling()
        if add_arrow:
            # arrows += [add_arrow]
            arrow_group.add(add_arrow)

        # for arrow in arrow_group:
        #     arrow.update(arrows)  # update the arrow such position and state

        # draw_map(map_array)
        # pygame.draw.line(window.screen, (255, 0, 0), (0, 300), (window.WIDTH, 300))

        # player handling
        player.draw(window.screen)
        player.move(moving_left, moving_right, world)

        # enemy handling
        enemy_group.update(player, window.screen, world, screen_scroll)
        enemy_group.draw(window.screen)
        # arrow handling
        arrow_group.update(window.screen, world, enemy_group, player)

        # coin handling
        coin_group.draw(window.screen)
        coin_group.update(player)  # check for player collision


        # tile groups
        decoration_group.draw(window.screen)
        decoration_group.update()

        waters_group.draw(window.screen)
        waters_group.update()

        # display text
        window.draw_text(f'weapon: {["Sword", "Bow"][player.current_weapon - 1]}', (10, 7))
        window.draw_text(f'Press [1] to use Sword, [2] to use Bow', (10, 20))

        pygame.display.update()  # make all the changes

        clock.tick(FPS)


if __name__ == "__main__":
    main(LEVEL)
