# EDIT FOR IMAGES: DIMENSIONS SHOULD BE 17x30
# if __name__ == 'Game_V4':
from entity_class import Entity, Enemy, Projectile, Player, Group
import pygame, WINDOW, QuestionWindow, os, sys, random, csv
from Items import AnimatedTile, Decoration, DeathBlock, Obstacle
from transition import ScreenFade

pygame.init()
read_json = WINDOW.read_json # using the pre-coded read and write methods to json files
write_json = WINDOW.write_json
x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

current_path = os.path.dirname(__file__)  # Where your .py file is located
image_path = os.path.join(current_path, 'images')  # The image folder path
coin_path = os.path.join(image_path, 'coin')

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)
LEVEL = 2
TILE_TYPES = os.listdir(f'images/level_images/{LEVEL}/Tiles')
img_list = []
TILE_SCALE = (window.TILE_DIMENSION_X, window.TILE_DIMENSION_Y)
tile_x, tile_y = TILE_SCALE
ENEMY = random.choice(['knight', 'samurai', 'stormy'])
ENEMY = 'stormy'
PLAYER = 'player'
# ENEMY_IMG = 'samurai'
# PLAYER_IMG = pygame.image.load(f'images/mobs/{PLAYER}/default.png')

background = pygame.transform.scale(pygame.image.load(WINDOW.get_path('backgrounds/background_2.png')),window.SIZE).convert_alpha()

GRAVITY = 0.75
# scale = (60,92) # with sword
# load in game data
tile_info = {
    'obstacle': '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 22 23'.split(),
    'decoration': '21 28'.split(),
    'kill_block': '26 27'.split(),
    'coin': '',
    'player': '24',
    'portal': '30',
    'enemy': '25',
    'enemy_scale': (int(70 * 2.4), 92),
    'player_scale': (50, 83),
    'move_radii': [3, 1, 2, 2, 0, 2, 0, 0, 1, 0, 1, 1],

}

enemy_scale = (int(70 * 2.4), 92)
player_scale = (50, 83)
move_radii = [0, 1, 2, 2, 0, 2, 0, 0, 1, 0, 1, 1]
img_list = {}
for i in TILE_TYPES:
    img = pygame.image.load(WINDOW.get_path(f'images/level_images/{LEVEL}/Tiles/{i}')).convert_alpha()
    name = i[:i.index('.')]
    img_list[name] = img


class World:
    def __init__(self):
        self.obstacle_list = []
        self.bg_scroll = 0
        self.no_collide = []  # blocks that shouldn't be checked for collision
        self.height = 0
        self.all_tiles = []

    def process_data(self, data):
        enemy_counter = 0
        player = Player(500, 500, 'player', player_scale, melee_dps=50)
        # iterate through each value in level data file
        decorations = []  # add in all the tiles that don't need to be checked for collision
        death_blocks = []
        enemies = []
        coins = []
        portals = []

        for ind, layer in enumerate(data.values()):
            for y, row in enumerate(layer):
                self.height = len(layer)
                for x, tile in enumerate(row):
                    if tile == '-1':
                        continue

                    # if 24 <= int(tile) <= 25:
                    #     tile = str(int(tile) - 2)
                    img = img_list[tile]  # get the image from the list of images
                    img_rect = img.get_rect()
                    # img_rect.topleft = (x * window.TILE_DIMENSION_X, y * window.TILE_DIMENSION_Y)
                    img_rect.bottomleft = (x * window.TILE_DIMENSION_X, y * window.TILE_DIMENSION_Y + 46)
                    img_mask = pygame.mask.from_surface(img)

                    obj = None
                    if tile in tile_info['obstacle']:
                        obj = Obstacle(img, img_rect)
                        if ind != 0: self.obstacle_list.append(obj) # if it isn't the 0th layer (for no collisions)
                    elif tile in tile_info['decoration']:  # grass / no collision decoration
                        obj = Decoration(img, img_rect)
                        # decorations.append(Decoration(img, img_rect))
                        # self.obstacle_list.append(obs) # add them onto the obstacle draw list
                    elif tile in tile_info['kill_block']:  # water
                        obj = DeathBlock(img, img_rect)
                        death_blocks.append(obj)
                    elif tile == tile_info['coin']:  # coin
                        obj = AnimatedTile('coin', img_rect.x, img_rect.y, (32, 32))
                        coins += [obj]
                    elif tile == tile_info['player']:  # create player if there's one on the map
                        # print('player')
                        player = Player(img_rect.x, img_rect.y, PLAYER, player_scale, melee_dps=1000)
                    elif tile == tile_info['enemy']:
                        enemies += [Enemy(img_rect.x, img_rect.y, ENEMY, enemy_scale,
                                          all_animations=['Idle', 'Die', 'Running', 'Attack'],
                                          max_health=100, x_vel=2, move_radius=tile_info['move_radii'][enemy_counter])]
                        enemy_counter += 1
                    elif tile == tile_info['portal']:
                        portals += [AnimatedTile('portal', img_rect.x,img_rect.y, 2)]
                    if obj: self.all_tiles.append(obj)
        return player, decorations, death_blocks, enemies, coins, portals

    def draw(self, background, target):
        background_width = background.get_width()
        for i in range(4):
            window.screen.blit(background, ((i * background_width) - self.bg_scroll, 0))

        for tile in self.all_tiles:
            temp = tile.rect.copy()
            x, y = target.rect.topleft
            temp.x = temp.x - x + window.WIDTH // 2
            temp.y = temp.y - y + window.HEIGHT // 2
            window.screen.blit(tile.image, temp)
            # pygame.draw.rect(window.screen, (255,0,0),temp,2)

# noinspection PyAssignmentToLoopOrWithParameter
def load_level(level):
    layers = {}
    path = f'levels/{level}'
    files = os.listdir(path)

    ordered = sorted(files,key=lambda i: int(i.split('_')[1][:i.split('_')[1].index('.')]))  # sort layers based on numbers
    # highest number == highest layer -> prioritised/placed above everything else
    # so by sorting from lowest -> highest, lowest layer is blitted first, and highest layer is blitted last/ on top of everything else

    files = ordered  # sort the tiles such that highest layer is prioritised/ blitted over the other layers
    for index, file in enumerate(files):
        with open(os.path.join(path, file)) as file:
            level = csv.reader(file, delimiter=',')
            layers[index] = [*level]
        # sys.exit()
    return layers

def show_summary(right, wrong, accuracy, streak, timer):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if window.check_return():
                    return

            if event.type == pygame.QUIT:
                return
        window.draw_text('right',(30,10),center=True)
    pass

class Camera:
    def __init__(self, target):
        self.rect = target.rect.copy()
        self.x, self.y = target.rect.topleft

    def update(self, target, world):
        if target.current_action not in target.combat_animations:
            # make sure the camera doesn't jitter after switching animations. Keeps the camera in place
            if target.direction == 1:
                self.rect.bottomleft = target.rect.bottomleft
            else:
                self.rect.bottomright = target.rect.bottomright

def play_level(username, user_id, level):
    game_level = load_level(LEVEL)
    world = World()
    # load in the questions
    question_data = read_json(f'Questions/{level}.json')
    # NOTE: question_data[question][username] = list(correct: int, incorrect: int, percentage: float)

    # select the 10 questions the user performed worst at, no longer random selection using sample alone
    questions = sorted(question_data, key=lambda question: (question_data[question][username])[2], reverse=True)[:10] # biggest -> smallest correct %
    questions = random.sample(questions, len(questions)) # shuffle the order of selected questions
    # questions will be treated as a stack. Last in is first out

    # sprite groups
    player, decorations, death_blocks, enemies, coins, portals = world.process_data(game_level)
    decoration_group = Group(*decorations)
    death_blocks_group = Group(*death_blocks)
    enemy_group = Group(*enemies)
    arrow_group = Group()
    coin_group = Group(*coins)
    portal_group = Group(*portals)
    camera = Camera(player)
    points = 0
    run=True

    show_question = False
    fade = ScreenFade(1, (0, 0, 0))
    start_fade = True
    x1 = pygame.time.get_ticks()
    timer = 0
    timing = 0
    portal_enter = False
    questions = questions[:len(enemy_group.sprites())]
    total_right = total_wrong = total_accuracy = 0
    streak = 0
    max_streak = 0
    while run:
        player.check_alive()
        camera.update(player, world)

        # only perform actions based on these conditions
        move_conditions = not player.in_air and player.health and (
                    player.y_vel <= player.GRAVITY) and not start_fade # making sure player isn't in the air and is still alive

        attack_conditions = not (
                player.sword_attack or player.bow_attack) and not start_fade  # only allow attacking if not already in attack animation -> ADD INTO ITERATIVE DEVELOPMENT

        window.refresh(show_mouse_pos=False,back=True,pos=(10,10))
        world.draw(background, camera)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

            # check for keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # level is not finished, therefore don't save changes
                    return

                if event.key == pygame.K_r:
                    enemy_group.regen()

                if event.key == pygame.K_h:
                    player.health = player.max_health

                # jumping
                # making sure the player is falling or jumping during
                if event.key == pygame.K_w and move_conditions and attack_conditions and not player.in_air and player.y_vel <= 0.75:
                    player.jumping = True

                # attacking
                if (event.key == pygame.K_SPACE) and move_conditions and attack_conditions:
                    if player.current_weapon == 1:  # sword selected
                        player.sword_attack = True
                    elif player.current_weapon == 2 and player.shoot_cooldown_timer == 0:  # bow selected
                        player.bow_attack = True
                        player.shoot_cooldown_timer = player.shoot_cooldown
                        pass
                # weapon selection
                value = chr(event.key)
                if value in ['1', '2']:
                    player.current_weapon = int(value)
                    pass

            # check for keys that are lifted/ no longer being pressed
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if window.check_return():
                    run = False
                    continue

        keys = pygame.key.get_pressed()

        # group handling
        moving_left = keys[pygame.K_a] and attack_conditions
        moving_right = keys[pygame.K_d] and attack_conditions

        # player handling
        add_arrow = player.animation_handling()
        if add_arrow: arrow_group.add(add_arrow)

        player.draw(window.screen, camera)
        player.move(moving_left, moving_right, world, death_blocks)
        player.update(moving_left, moving_right, world)

        # enemy handling
        enemy_group.update(player, window.screen, world)
        enemy_group.draw(window.screen, target=camera)

        # arrow handling
        arrow_group.update(window.screen, world, enemy_group, player, camera)
        arrow_group.draw(window.screen, target=camera)

        death_blocks_group.draw(window.screen, target=camera)
        death_blocks_group.update(player)  # do death block checking for player

        # # coin handling
        coin_group.draw(window.screen, target=camera)
        coin_group.update(player, camera)  # check for player collision

        # portal handling
        portal_group.draw(window.screen, target=camera)
        # if the user hasn't already entered the portal
        for portal in portal_group.sprites():
            portal_collision = portal.update(player,camera) and not portal_enter
            if portal_collision and (not questions or not enemy_group.sprites()): # if all questions are answered or enemies are dead
                start_fade = True
                fade.direction = -1
                show_question=False
                portal_enter = True

        # do fade animation
        if start_fade:
            if fade.fade(window.screen): # if the fade has completed
                start_fade = False # don't show the intro fade anymore
                if portal_enter and fade.direction == -1:
                    run = False
                    show_question = False
                # if fading out, check if there are still questions and enemies left to show a question, otherwise its just a normal fade
                elif fade.direction == -1 and not player.remove:
                    show_question = True
                # if the player has died, then don't update their timer
                elif fade.direction == -1 and player.remove:
                    run = False
                    timer = 0
                    start_fade = False

        if show_question:
            if questions: # making sure there are still questions left to pop
                current_question = questions.pop() # pop the question at the top of the stack
                QuestionWindow_values = QuestionWindow.StartQuestion(question=current_question, question_data=question_data, timer=timer,x1=x1)

                # extract current stats for the question and adjust them based on result of the user's choice
                if isinstance(QuestionWindow_values, tuple): # if the result and timer was returned
                    result = QuestionWindow_values[0] # the outcome of the question displayed
                    user_right, user_wrong, user_accuracy = (question_data[current_question])[username]
                    if result: user_right += 1; points += 10; total_right+=1; streak += 1 # if they got the question right, add 10 points
                    else: user_wrong += 1; total_wrong += 1; streak = 0; max_streak = max(streak,max_streak)
                    if user_wrong!=0 or user_right!=0:
                        user_accuracy = user_right/(user_right+user_wrong) # to ensure that the denominator is not 0
                        total_accuracy = total_right/(total_right+total_wrong)
                    question_data[current_question][username] = [user_right, user_wrong, user_accuracy] # update statistics of the user on the question displayed
                    timer = QuestionWindow_values[1]
                else:
                    timer = QuestionWindow_values

                # inwards fade
                start_fade = True
                fade.direction = 1
                show_question = False

        # start fade animation if player has died
        if player.remove and not start_fade:
            start_fade = True
            fade.direction = -1

         # if an enemy has died, present a question
        enemy_dead = enemy_group.check_death()
        if enemy_dead and questions: # if there are still questions left, then do the animation to goto question screen
            start_fade = True
            fade.direction = -1

        if (pygame.time.get_ticks() - x1) > 1000: # 1 ticks == 1 millisecond, 1000 millisecond = 1 second
            timer += 1  # account for the time in the question screen
            x1 = pygame.time.get_ticks()

        # draw text and back button
        window.draw_text(text=f'Time: {WINDOW.convert_time_format(timer)}', pos=(670,3), size='MEDIUM', center=(True,False))
        window.draw_back()
        window.draw_text(f'weapon: {["Sword", "Bow"][player.current_weapon - 1]}', (200, 5))

        pygame.display.update()  # make all the changes
        clock.tick(FPS)
    # show the user their summary statistics:
    show_summary(total_right, total_wrong, total_accuracy, max_streak, timer)
    # update question data and user data when/ if run == False, if they just finished level/died
    write_json(question_data, f'Questions/{level}.json')
    user_info = read_json(f'user_info/users.json')
    current_best = user_info[username][level]

    # only update the completion time if the user answered all the questions/ defeated all enemies and they didn't just instantly die
    if current_best != 0 and (not questions or not enemy_group.sprites()) and timer:
        current_best = min(current_best, timer)
    elif current_best == 0 and timer:
        current_best = timer

    user_info[username][level] = current_best # update time if it was lower
    user_info[username]['points'].append(points) # adding points onto the player's history for graph plotting
    write_json(user_info, f'user_info/users.json') # save all the changes

def main(username, user_id, level):
    play_level(username, user_id, level)

if __name__ == '__main__':
    main('Testing1', 0, 2)
