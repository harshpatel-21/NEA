import os, sys, csv

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
# print(x)
sys.path.insert(1, x)

# EDIT FOR IMAGES: DIMENSIONS SHOULD BE 17x30
# if __name__ == 'Game_V4':
from entity_class import Entity, Enemy, Projectile, Player, Group
import pygame, WINDOW
from Items import Item, Decoration, DeathBlock, Obstacle

pygame.init()

x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

current_path = os.path.dirname(__file__)  # Where your .py file is located
image_path = os.path.join(current_path, 'images')  # The image folder path
coin_path = os.path.join(image_path, 'coin')

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)
LEVEL = 2
TILE_TYPES = os.listdir(f'images/level_images/{2}/Tiles')
img_list = []
TILE_SCALE = (window.TILE_DIMENSION_X, window.TILE_DIMENSION_Y)
tile_x, tile_y = TILE_SCALE
ENEMY = 'samurai'
PLAYER = 'player'
# ENEMY_IMG = 'samurai'
# PLAYER_IMG = pygame.image.load(f'images/mobs/{PLAYER}/default.png')

background = pygame.transform.scale(pygame.image.load(WINDOW.get_path('backgrounds/background_2.png')),window.SIZE).convert_alpha()

GRAVITY = 0.75

# scale = (60,92) # with sword
# load in game data
tile_info = {
    'obstacle': '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 22 23',
    'decoration': '21 28',
    'kill_block': '26 27',
    'coin': '',
    'player': '24',
    'enemy': '25',
}

enemy_scale = (int(70 * 2.4), 92)
player_scale = (50, 83)
move_radii = [1, 1, 1, 1, 1]
img_list = {}
for i in TILE_TYPES:
    img = pygame.image.load(WINDOW.get_path(f'images/level_images/{LEVEL}/Tiles/{i}')).convert_alpha()

    name = i[:i.index('.')]
    img_list[name] = img

class World:
    def __init__(self):
        self.obstacle_list = []
        self.bg_scroll = 0
        self.no_collide = [] # blocks that shouldn't be checked for collision
        self.layers = None
        self.all_tiles = []

    def process_data(self, data):
        enemy_counter = 0
        player = Player(500, 500, 'player', player_scale, melee_dps=25)
        # iterate through each value in level data file
        decorations = []  # add in all the tiles that don't need to be checked for collision
        death_blocks = []
        enemies = []
        coins = []

        for ind, layer in enumerate(data.values()):
            # print(layer)
            for y, row in enumerate(layer):
                world.layers = len(layer)
                for x, tile in enumerate(row):
                    if tile == '-1':
                        continue

                    # if 24 <= int(tile) <= 25:
                    #     tile = str(int(tile) - 2)
                    img = img_list[tile]  # get the image from the list of images
                    img_rect = img.get_rect()
                    img_rect.topleft = (x * window.TILE_DIMENSION_X, y * window.TILE_DIMENSION_Y)
                    img_rect.bottomleft = (x * window.TILE_DIMENSION_X, y * window.TILE_DIMENSION_Y + 46)
                    img_mask = pygame.mask.from_surface(img)
                    tile_data = (img, img_rect, img_mask)
                    obj = None
                    if tile in tile_info['obstacle']:
                        obj = Obstacle(img, img_rect)
                        self.obstacle_list.append(obj)
                    elif tile in tile_info['decoration']:  # grass / no collision decoration
                        obj = Decoration(img, img_rect)
                        # decorations.append(Decoration(img, img_rect))
                        # self.obstacle_list.append(obs) # add them onto the obstacle draw list
                    elif tile in tile_info['kill_block']:  # water
                        obj = DeathBlock(img, img_rect)
                        death_blocks.append(obj)
                    elif tile == tile_info['coin']:  # coin
                        obj = Item('coin', img_rect.x, img_rect.y, (32, 32))
                        coins += [obj]
                    elif tile == tile_info['player']:  # create player if there's one on the map
                        # print('player')
                        player = Player(img_rect.x, img_rect.y, PLAYER, player_scale, melee_dps=30)
                    elif tile == tile_info['enemy']:
                        enemies += [Enemy(img_rect.x, img_rect.y, ENEMY, enemy_scale,
                                          all_animations=['Idle', 'Die', 'Running', 'Attack'],
                                          max_health=100, x_vel=2, move_radius=1)]
                    if obj: self.all_tiles.append(obj)
        return player, decorations, death_blocks, enemies, coins

    def draw(self, background, target):
        background_width = background.get_width()
        for i in range(4):
            window.screen.blit(background, ((i * background_width) - self.bg_scroll, 0))

        for tile in self.all_tiles:
            temp = tile.rect.copy()
            x,y = target.rect.topleft
            temp.x = temp.x - x + window.WIDTH//2
            temp.y = temp.y - y + window.HEIGHT//2
            window.screen.blit(tile.image, temp)
            # pygame.draw.rect(window.screen, (255,0,0),temp,2)

# noinspection PyAssignmentToLoopOrWithParameter
def load_level(level):
    layers = {}
    path = f'levels/{level}'
    files = os.listdir(path)
    entities = []
    for file in files:
        if 'Entities' in file:
            entities = file
            files.remove(file)
    ordered = sorted(files, key=lambda i: int(i.split('_')[1][:i.split('_')[1].index('.')])) # sort layers based on numbers
    files = ordered  # sort the tiles such that highest layer is prioritised/ blitted over the other layers

    for index, file in enumerate(files):
        with open(os.path.join(path, file)) as file:
            level = csv.reader(file, delimiter=',')
            layers[index] = [*level]

    with open(os.path.join(path, entities)) as file: # at the very last layer, store the players
        level = csv.reader(file, delimiter=',')
        layers[len(layers)] = [*level]
        # sys.exit()
    return layers


game_level = load_level(2.1)
# print(game_level)
world = World()


def draw_grid(scroll):
    tiles_x, tiles_y = window.TILE_DIMENSION_X, window.TILE_DIMENSION_Y
    lines_x = background.get_width() // tiles_x
    lines_y = background.get_height() // tiles_y

    # vertical lines
    for j in range(window.MAX_BLOCKS_X + 1):
        x = (j * tiles_x)
        pygame.draw.line(window.screen, (200, 200, 200), (x + scroll, 0), (x + scroll, background.get_height()))

    # horizontal liens
    for i in range(lines_y + 1):
        y = (i * tiles_y)
        pygame.draw.line(window.screen, (200, 200, 200), (0 + scroll, y), (window.WIDTH * 4 + scroll, y))

class Camera:
    def __init__(self, target):
        self.rect = target.rect.copy()
        self.x, self.y = target.rect.topleft

    def update(self, target):

        if target.current_action not in target.combat_animations:
            # make sure the camera doesn't jitter after switching animations. Keeps the camera in place
            if target.direction == 1:
                self.rect.bottomleft = target.rect.bottomleft
            else:
                self.rect.bottomright = target.rect.bottomright

def main(level):
    # scale = (60,92) # with sword
    # player = Player(100, 100, 'player', scale, melee_dps=15)
    # enemy = Player(500,100,'enemy',scale,all_animations = ['Idle','Die'],max_health = 50 )
    player, decorations, death_blocks, enemies, coins = world.process_data(game_level)
    # print(world.obstacle_list)
    # print(enemies)
    # print(decorations)
    # enemy_1 = Enemy(500, 0, 'samurai', (int(70 * 2.4), 92), all_animations=['Idle', 'Die', 'Running', 'Attack'],
    #                 max_health=100, x_vel=2)
    # enemy_2 = Enemy(700, 0, 'knight', player_scale, all_animations=['Idle', 'Running', 'Attack', 'Die'],max_health=10, x_vel=2)
    # enemy_3 = Enemy(400, 0, 'enemy', (int(70 * 2.4), 92), all_animations=['Idle', 'Die', 'Run', 'Attack'],
    #                 max_health=100, x_vel=2)
    # enemy_1.move_radius = 2
    # enemy_2.move_radius = 5
    # player.current_weapon_damage = {1: 35, 2: 50}
    # enemy_group.add(enemy_1,enemy_2)
    # enemies.append(enemy_1)
    # enemies.append(enemy_2)
    # sprite groups
    decoration_group = Group(*decorations)
    death_blocks_group = Group(*death_blocks)
    enemy_group = Group(*enemies)
    arrow_group = Group()
    coin_group = Group(*coins)
    print(enemy_group, decoration_group, death_blocks_group)
    arrows = []
    # enemies = [enemy_1, enemy_2]
    # coin_group = pygame.sprite.Group()

    # enemy_1.direction = -1
    player.weapon = 1
    player.x_vel = 6
    screen_scroll = 0  # respective to player movement
    background_scroll = 0  # cumulative value
    moving_left = moving_right = False
    dust_pos = ()
    camera = Camera(player)
    while True:
        if player.remove:
            return
        camera.update(player)
        # only perform actions based on these conditions
        move_conditions = not(player.in_air) and (player.health) and (player.y_vel <= player.GRAVITY)  # making sure player isn't in the air and is still alive
        
        attack_conditions = not (
                player.sword_attack or player.bow_attack)  # only allow attacking if not already in attack animation -> ADD INTO ITERATIVE DEVELOPMENT
        window.refresh()
        world.draw(background, camera)
        # draw_grid(0)

        draw_dust = False
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
                    player.health = player.max_health

                # jumping
                # making sure the player is falling or jumping during
                if event.key == pygame.K_w and move_conditions and attack_conditions and not player.in_air and player.y_vel <= 0.75:
                    # print(pygame.time.get_ticks())
                    player.jumping = True
                    draw_dust = True
                    player.particle_counter = 0 # trigger dust animation
                    # player.in_air = True

                # attacking
                if (event.key == pygame.K_SPACE) and move_conditions and attack_conditions:
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
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                pass

        keys = pygame.key.get_pressed()

        moving_left = keys[pygame.K_a] and attack_conditions
        moving_right = keys[pygame.K_d] and attack_conditions


        # creating an arrow instance if bow animation was activated
        add_arrow = player.animation_handling()
        if add_arrow:
            # arrows += [add_arrow]
            arrow_group.add(add_arrow)

        for arrow in arrow_group:
            arrow.update(arrows, world, enemy_group, player)  # update the arrow such position and state

        # draw_map(map_array)
        # pygame.draw.line(window.screen, (255, 0, 0), (0, 300), (window.WIDTH, 300))

        # player handling
        player.draw(window.screen, camera)
        screen_scroll = player.move(moving_left, moving_right, world, death_blocks)
        player.update(moving_left, moving_right, world)

        # enemy handling
        enemy_group.update(player, window.screen, world)
        enemy_group.draw(window.screen, camera)
        # arrow handling
        arrow_group.update(window.screen, world, enemy_group, player)
        arrow_group.draw(window.screen, camera)
        #
        # # coin handling
        # coin_group.draw(window.screen, screen_scroll)
        # coin_group.update(player)  # check for player collision
        #

        # tile groups
        decoration_group.draw(window.screen)
        decoration_group.update()
        #
        death_blocks_group.draw(window.screen)
        death_blocks_group.update(player) # do death block checking for player

        # death_blocks_group.update(enemy_group) # do death block checking for enemies

        # display text
        window.draw_text(f'weapon: {["Sword", "Bow"][player.current_weapon - 1]}', (10, 7))
        window.draw_text(f'Press [1] to use Sword, [2] to use Bow', (10, 20))
        # world.bg_scroll -= screen_scroll
        # if draw_dust:
        #     print('jumping')
        if player.particle_counter == 0:
            dust_pos = (player.rect.x, (player.rect.y//46)*46 + 92)
        player.draw_dust(window.screen, dust_pos)
        pygame.display.update()  # make all the changes

        clock.tick(FPS)


if __name__ == "__main__":
    while 1:
        window.refresh()
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if chr(event.key) == 'r' or chr(event.key)=='s':
                    main(LEVEL)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    break

        pygame.display.update()
        # if inp == 'r':
        #     main(LEVEL)
