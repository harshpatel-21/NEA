import pygame, sys, os, random, inspect

x = '\\'.join(os.path.abspath(__file__).split('\\')[:-2])  # allow imports from main folder
sys.path.insert(1, x)

from WINDOW import Display

# websites:
# https://www.piskelapp.com/
# https://pixlr.com/x/#home

pygame.init()
JUMP_Y = 15


class Tile:
    def __init__(self, image, rect, mask):
        self.rect = rect
        self.mask = mask
        self.image = image
        self.direction = 0


class Projectile(pygame.sprite.Sprite):
    def __init__(self, shooter, image='Arrow04'):
        pygame.sprite.Sprite.__init__(self)
        self.shooter = shooter
        self.image = pygame.image.load(f'images/{image}.png').convert_alpha()
        self.image = pygame.transform.flip(self.image, shooter.direction == -1, False)
        self.rect = self.image.get_rect()
        self.rect.topleft = (shooter.rect.x, shooter.rect.y)
        self.direction = shooter.direction

        if self.direction == 1:  # adjusting starting position of arrow
            self.rect.x += shooter.rect.w
        else:
            self.rect.x -= self.rect.w

        self.rect.y = shooter.rect.center[1] - 5
        self.x_vel = 14
        self.acceleration = 2.5
        self.mask = pygame.mask.from_surface(self.image)
        self.remove = False

    def draw(self, surface, target):
        temp = self.rect.copy()
        temp.x = temp.x - target.rect.x + Display.WIDTH // 2
        temp.y = temp.y - target.rect.y + Display.HEIGHT // 2
        surface.blit(self.image, temp)

    def update(self, surface, world, enemy_group, player, arr=None):
        self.check_collision(enemy_group)  # check for collision with enemies
        self.check_collision(player)  # check for collision with player

        if not self.remove: self.rect.x += (self.x_vel * self.acceleration) * self.direction
        # self.acceleration -= 0.035*self.acceleration
        self.acceleration *= 0.85

        # check if the arrow has gone off the screen or low acceleration
        if (self.rect.left > Display.WIDTH) or (self.rect.right < 0) or self.acceleration < 0.08:
            self.remove = True  # set the flag to remove the arrow to true
            # self.direction *= -1

        # check for tile collision
        for tile in filter(lambda i: i not in world.no_collide, world.obstacle_list):
            if self.mask_collision(tile):
                self.remove = True

                pass
        if self.remove:
            # arr.remove(self) # used when arrows were stored in an array
            self.kill()  # frees up memory and removes all instances of this specific arrow from associated groups

    def check_collision(self, objs):  # checking for arrow collision from bow_attack
        # flip the mask of the image during collision detection
        if isinstance(objs, Group):
            for obj in objs:
                if self.entity_collision(obj):
                    self.remove = True

        elif isinstance(objs, Player):
            if self.entity_collision(objs):
                self.remove = True

    def entity_collision(self, obj):
        collision = self.mask_collision(obj)
        # change border color if collision with arrow has occurred
        if collision:
            obj.border_color = (0, 255, 0)
            self.remove = True
            self.kill()
            obj.health2 = obj.health
            obj.health -= self.shooter.current_weapon_damage.get(
                self.shooter.current_weapon)  # do damage based on current weapon
            obj.difference = max(0, obj.health2 - obj.health)
            # self.shooter.bow_attack = False
        else:
            obj.border_color = (255, 0, 0)
        return collision

    def mask_collision(self, obj):
        obj_mask = pygame.mask.from_surface(pygame.transform.flip(obj.image, obj.direction == -1, False))
        offset_x = obj.rect.x - self.rect.x
        offset_y = obj.rect.y - self.rect.y
        collision = self.mask.overlap(obj_mask, (offset_x, offset_y))
        return collision


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, obj_type, scale, max_health=100, x_vel=6, all_animations=None, combat_animations=None,
                 bow_dps=20,
                 melee_dps=33):
        self.GRAVITY = JUMP_Y / 20
        self.all_animations = all_animations
        self.combat_animations = combat_animations
        if all_animations is None and obj_type == 'player':
            self.all_animations = ['Idle', 'Running', 'Jumping', 'Falling', 'Melee', 'Bow', 'Die']
        if combat_animations is None and obj_type == 'player':
            self.combat_animations = [self.get_index('Melee'), self.get_index('Bow')]
        pygame.sprite.Sprite.__init__(self)
        self.max_health = max_health
        self.health = self.max_health
        self.y_vel = 0
        self.obj_type = obj_type
        self.animations = []
        self.animation_pointer = 0
        self.current_action = 0
        self.time1 = pygame.time.get_ticks()
        for animation in self.all_animations:
            self.get_animations(obj_type, animation, scale)
        self.image = self.animations[self.current_action][self.animation_pointer]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.x_vel = x_vel
        self.direction = 1  # [1,-1] = [facing right, facing left]
        self.flip_image = False
        self.jumping = False
        self.in_air = True
        self.sword_attack = False
        self.bow_attack = False
        self.current_weapon = 1  # 1 == sword, 2 == Bow
        self.shoot_cooldown = 10
        self.shoot_cooldown_timer = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.border_color = (255, 0, 0)
        self.collisions = 0
        self.health2 = self.health
        self.difference = self.health - self.health2
        self.current_weapon_damage = {1: melee_dps, 2: bow_dps}  # sword deals 50 damage, bow deals 20
        self.increase_health = 0
        self.health_rect = pygame.Rect((x, y, 70, 6))
        self.health_rect.center = self.rect.center
        self.health_rect.y -= self.rect.h // 2 + 10
        self.dust = False  # i don't want the player to start off with dust
        self.particle_counter = 10000
        self.dust_time = pygame.time.get_ticks()
        self.ground = 0
        self.dust = False
        self.remove = False

    def move(self, moving_left, moving_right, world, death_blocks=0):  # handle player movement
        self.health_rect.y = self.rect.y - 10
        scroll_threshold = 400
        screen_scroll = 0
        # reset movement variables
        dx = dy = 0
        check = True
        if not self.check_alive():  # if the player is dead, then don't do any movements
            return
        # horizontal movement
        if self.bow_attack:  # don't allow movement during an attack animation
            check = False

        if moving_left and check:
            dx = -self.x_vel
            self.flip_image = True
            self.direction = -1

        if moving_right and check:
            dx = self.x_vel
            self.flip_image = False
            self.direction = 1

        # jumping/vertical movement
        if self.jumping and (not self.in_air) and check:
            self.y_vel = -JUMP_Y
            self.jumping = False
            self.in_air = True

        # gravity/ downward acceleration
        y1 = self.y_vel
        self.y_vel = min(self.y_vel + self.GRAVITY, 10)
        dy += self.y_vel

        if y1 < 0 and self.y_vel > 0:  # if the player was jumping and is now falling, after landing dust should show
            self.dust = True
        # check collision with floor
        # self.rect.w = 48
        # self.rect.h = 80
        for tile in world.obstacle_list:
            # check collision in x direction
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.w, self.rect.h):
                dx = 0
                # If AI collision with wall, turn em around
                if isinstance(self, Enemy):
                    # self.direction *= -1
                    # self.move_counter *= -1
                    self.wall_collision = True

            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.w, self.rect.h):
                dy = 0
                # check if jumping and below ground
                if self.y_vel < 0:
                    self.y_vel = 0
                    self.rect.top = tile.rect.bottom

                # if they are falling
                elif self.y_vel > 0:
                    self.ground = min(5, self.ground + 1)
                    self.y_vel = 0
                    self.in_air = False
                    self.rect.bottom = tile.rect.top
                    if self.ground == 1 or self.dust: self.particle_counter = 0; self.dust = False  # after landing, don't

        # check if going off the sides
        if self.rect.y > (world.height) * 46 - self.rect.h:  # if the player is off screen
            self.remove = True
            self.kill()
            self.update_action(self.get_index('Die'))
            return

        # update player position
        self.rect.x += dx
        self.rect.y += dy
        self.health_rect.x += dx
        self.health_rect.y += dy

        return screen_scroll

    def reset(self):
        # self.current_action = self.get_index('Idle')
        # if self.animation_pointer == len(self.all_animations[self.get_index('Die')])-1:self.kill()
        return

    def draw_health_bar(self, surface, target):

        # self.health_rect.center = self.rect.center
        # self.health_rect.y -= self.rect.h//2 + 10
        temp = self.rect.copy()  # copy the rect of the current entity

        temp.x = temp.x - target.rect.x + Display.WIDTH / 2.0
        temp.y = temp.y - target.rect.y + Display.HEIGHT // 2 - 10

        health_bar_dx = 4 * [-1, 1][self.increase_health > 0]
        x_padding = {
            'player': 10,
            'samurai': 13
        }
        if not self.check_alive():  # if the entity is dead, don't draw a health bar
            return

        self.health_rect.midtop = temp.midtop
        if self.direction == -1 and isinstance(self, Enemy):  # adjusts the position of the health bar if need be
            self.health_rect.topright = temp.topright

        pygame.draw.rect(surface, (255, 0, 0), self.health_rect)
        current_health = self.health_rect.copy()
        current_health.w = (self.health / self.max_health) * self.health_rect.w  # the % of health * full width
        pygame.draw.rect(surface, (0, 255, 0), current_health)
        pygame.draw.rect(surface, (0, 0, 0), self.health_rect, 3)

    def animation_handling(self):  # updates the animation frame
        self.check_alive()
        self.shoot_cooldown_timer = max(0, self.shoot_cooldown_timer - 1)  # makes sure the cooldown doesn't go below 0
        # update animation based on a timer since last time recorded
        cooldown_time = 90  # every 120 main game loops change animation frame
        if self.current_action in self.combat_animations:
            cooldown_time = 90
        # if self.current_action == 4 and self.obj_type == 'player':
        #     cooldown_time = 60
        if self.current_action == 2 and self.obj_type == 'samurai':
            cooldown_time = 90
        # if self.current_action == 1 and self.obj_type == 'knight':
        #     cooldown_time = 90
        shoot_projectile = False
        # update entity image
        self.image = self.animations[self.current_action][self.animation_pointer]
        image_rect = self.image.get_rect()

        if self.direction == 1:
            image_rect.bottomleft = self.rect.bottomleft  # keep the entity on the ground
        else:
            image_rect.bottomright = self.rect.bottomright

        self.rect = image_rect
        self.mask = pygame.mask.from_surface(self.image)
        current_time = pygame.time.get_ticks()
        death_index = self.get_index('Die')
        if (current_time - self.time1) > cooldown_time:
            self.animation_pointer += 1  # add one to animation pointer
            if self.current_action in self.combat_animations:  # if its a combat animation
                if self.animation_pointer >= len(
                        self.animations[self.current_action]):  # if at the last frame of animation
                    self.sword_attack = False  # no longer attacking with a weapon
                    if self.bow_attack:  # if currently in bow animation, set finished bow_animation to True
                        self.shoot_cooldown_timer = self.shoot_cooldown
                        shoot_projectile = True
                    self.bow_attack = False  # no longer attacking with a weapon
                    self.animation_pointer = 0  # reset animation pointer
                    self.current_action = 0  # go back to idle position

            elif self.current_action == death_index:  # death animation
                if self.animation_pointer > len(self.animations[death_index]) - 1:
                    self.animation_pointer = len(self.animations[death_index]) - 1
                    self.remove = True

            else:  # looping animations
                self.animation_pointer = self.animation_pointer % len(self.animations[self.current_action])

            self.time1 = pygame.time.get_ticks()

        if shoot_projectile:
            arrow = self.shoot()
            if arrow:
                return arrow

    def shoot(self):
        return Projectile(self)  # return an Projectile object

    def update_action(self, new_action, world=None):
        """ check if the new action is different to the new action
        # if the new action is the same as the old action, it would set animation pointer to 0 every time so only the
        # first frame of the animation would be shown. By adding this check, it makes it so that the animation pointer and animation is changed/reset
        # only if there is a change in the player action. """

        melee_index = self.get_index('Melee')
        if new_action == melee_index and world:
            # print('here')
            images = self.animations[melee_index]
            if any(self.check_image_collision(image, world) for image in
                   images):  # if wall collisions have occured in any of the frames
                self.sword_attack = False
                return

        if new_action != self.current_action:
            self.current_action = new_action
            # reset the index at which the animation for the specific action starts at
            self.animation_pointer = 0
            self.time1 = pygame.time.get_ticks()

    def update(self, moving_right, moving_left, world):
        # update player animations
        if self.obj_type == 'player':
            if self.in_air or self.y_vel > self.GRAVITY:  # if jumping or falling the 0.75 is due to gravity
                if self.y_vel < 0:  # if going upwards
                    self.update_action(self.get_index('Jumping'))
                    pass
                else:  # if falling
                    self.update_action(self.get_index('Falling'))
                    pass
            elif self.sword_attack:
                self.update_action(self.get_index('Melee'),
                                   world)  # if switchin g to sword animation, make sure new image doesn't collide with walls
            elif self.bow_attack:
                self.update_action(self.get_index('Bow'), world)  # if switching
            elif moving_right or moving_left:
                self.update_action(self.get_index('Running'))
            else:
                self.update_action(self.get_index('Idle'))
            return
        if self.obj_type == 'knight':
            if self.health:  # if the player is alive
                if self.in_air:  # if jumping
                    if self.y_vel < 0:  # if going upwards
                        self.update_action(self.get_index('Jumping'))
                        pass
                    else:  # if falling
                        self.update_action(self.get_index('Falling'))
                        pass
                elif self.sword_attack:  # if player is attacking with sword
                    self.update_action(self.get_index('Melee'), world)
                elif self.bow_attack:  # if player is attacking with a bow
                    self.update_action(self.get_index('Bow'), world=0)
                elif moving_right or moving_left:
                    self.update_action(self.get_index('Running'))  # set the animation to run
                else:
                    self.update_action(
                        self.get_index('Idle'))  # set back to idle animation if no other action is being performed

    def check_image_collision(self, image, world):
        image_rect = image.get_rect()
        if self.direction == 1:
            image_rect.bottomleft = self.rect.bottomleft  # keep the entity on the ground
        else:
            image_rect.bottomright = self.rect.bottomright

        for tile in world.obstacle_list:
            if image_rect.colliderect(tile.rect):
                return True
        return False

    def get_animations(self, obj_type, animation, scale):  # add animations for this sprite into a list
        animation_scale = {
            'player': {
                'Bow': (scale[0] * 1.6, scale[1]),
                'Melee': (scale[0] * 1.4, scale[1]),
                'Idle3': (scale[0] * 5, scale[1]),
                'Idle2': (scale[0] * 1.4, scale[1]),
                'Idle': (48, scale[1]),
                'Die': (scale[0] * 1, scale[1] * 0.8),
                'Running2': (scale[0] * 1.4, scale[1]),
                'Running': (48, scale[1]),
                'Jumping': (48, scale[1]),
                'Falling': (48, scale[1])
            },
            'samurai': {
                'Idle': (scale[0] * 0.5, scale[1] * 1),
                'Die': (scale[0] * 1.2, scale[1] * 0.95),
                'Running': (scale[0] * 0.5, scale[1]),
                'Attack': (scale[0] * 1.2, scale[1])
            },
            'knight': {
                'Idle': (46, 92),
                'Attack': (scale[0] * 2.7, scale[1] * 1.2),
                'Jumping': (46, 92),
                'Falling': (46, 92),
                'Running': (46 * 1.5, 92),
                'Die': (135, 60)
            }
        }
        temp = []
        img_path = f"images/mobs/{obj_type}/{animation}"
        get_img = 'os.path.join(img_path,image)'  # get a list of the image names for the animation
        images = os.listdir(img_path)
        for image in images:  # iterate through the images in this directory
            scale2 = scale
            scale_info = animation_scale.get(obj_type)
            if scale_info:
                scale_data = scale_info.get(animation)
                if scale_data: scale2 = [*map(int, scale_data)]
            scale2 = [*map(int, (scale2[0] * 0.8, scale2[1] * 0.8))]
            temp += [pygame.transform.scale(pygame.image.load(eval(get_img)),
                                            scale2).convert_alpha()]
        self.animations += [temp]

    def draw(self, surface, target):
        temp = self.rect.copy()
        temp.x = temp.x - target.rect.x + Display.WIDTH / 2.0
        temp.y = temp.y - target.rect.y + Display.HEIGHT // 2
        surface.blit(pygame.transform.flip(self.image, self.flip_image or self.direction == -1, False), temp)
        # pygame.draw.rect(surface, self.border_color, temp, 1)

        self.draw_health_bar(surface, target)

    # pygame.draw.rect(surface,self.border_color,self.rect,2)
    def draw_dust(self, surface, dust_pos):
        cooldown_time = 30
        images = os.listdir('images/dust')
        if self.particle_counter >= len(images):
            return
        # print(images)
        # if not self.particle_counter: return
        img = pygame.transform.flip(pygame.image.load(f'images/dust/{images[self.particle_counter]}').convert_alpha(),
                                    False, True)
        img_rect = img.get_rect()
        img_rect.y = (self.rect.y // 46) * 46 + 92
        img_rect.x = self.rect.x
        # print(img_rect,self.rect)
        surface.blit(img, dust_pos)
        current_time = pygame.time.get_ticks()

        if (current_time - self.dust_time) >= cooldown_time:
            # print(self.particle_counter)
            self.dust_time = current_time
            # print('next')
            self.particle_counter = min(self.particle_counter + 1, len(images))
            # self.particle_counter = (self.particle_counter+1) % len(images)

    def check_alive(self):  # check if the entity is alive
        if self.health <= 0:  # if they've died
            self.health = 0  # health is back at 0
            x = self.get_index('Die')  # get the index of where the 'Die' animation is
            self.update_action(x)  # update the series of images that contain the death animation
        return self.health > 0

    def get_index(self, animation):  # get the death index from the list of animations
        index = None
        if animation in self.all_animations:
            index = self.all_animations.index(animation)
        return index

    def sword_collision(self, obj):  # check for sword attack collision
        if self.check_collision(obj) and obj.sword_attack:
            self.collisions += 1 and obj.sword_attack and self.direction != obj.direction
            self.health -= obj.current_weapon_damage.get(
                obj.current_weapon) / 25
            return 1
        return 0

    def check_collision(self, obj):
        if self.health <= 0:
            return
        obj_mask = pygame.mask.from_surface(pygame.transform.flip(obj.image, obj.direction == -1,
                                                                  False))  # flips the mask of the image during collision detection
        offset_x = obj.rect.x - self.rect.x
        offset_y = obj.rect.y - self.rect.y
        current_mask = pygame.mask.from_surface(pygame.transform.flip(self.image, self.direction == -1,
                                                                      False))  # flips the mask of the image during collision detection
        collision = current_mask.overlap(obj_mask, (
            offset_x, offset_y))  # making sure player is in sword animation
        return bool(collision)


class Player(Entity):
    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)


class Enemy(Entity):
    def __init__(self, x, y, obj_type, scale, max_health=100, x_vel=5, all_animations=None, attack_radius=100,
                 move_radius=3, melee_dps=30):
        super().__init__(x, y, obj_type, scale, max_health, x_vel, all_animations, melee_dps=melee_dps)
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.attack_vision = pygame.Rect(0, 0, attack_radius, 20)
        self.combat_animations = [self.get_index('Attack')]
        self.attacked = False
        self.wait = 0
        self.change_direction = False
        self.wall_collision = False
        self.move_radius = move_radius
        self.trigger = False

    def rec_collision(self, obj):
        return self.attack_vision.colliderect(obj.rect)

    def start_attack(self, obj, world):
        if self.wait == 0 and self.rec_collision(obj) and self.check_alive():
            self.sword_attack = True
            self.update_action(self.get_index('Attack'), world)  # change the animation to attack animation
            self.wait = 100
            return True
        return False

    def AI(self, world, target):
        if self.in_air:  # if the enemy is falling
            self.move(0, 0, world)  # don't move in any direction
            return  # don't do anything else related to AI movement
        self.wait = max(0, self.wait - 1)

        AI_moving_right = False
        if self.sword_attack:
            return

        # set up attack radius
        self.attack_vision.center = self.rect.center
        if self.direction == 1:
            self.attack_vision.left = self.rect.right
        else:
            self.attack_vision.right = self.rect.left

        if self.check_alive():
            # checking if enemy is not already idling and not falling/jumping
            if random.randint(1, 500) == 1 and not self.idling and not self.in_air:
                self.set_idling(world)
                pass

            # if the enemy is in idling motion:
            if self.idling:
                # self.update_action(0)
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False
                    if self.change_direction:
                        self.direction *= -1
                        self.move_counter *= -1

                    # self.health_rect.x += scroll
                return  # don't attempt to move the player in idling animation

            if self.direction == 1:
                AI_moving_right = True

            AI_moving_left = not AI_moving_right
            self.move(AI_moving_left, AI_moving_right, world)
            self.update_action(self.get_index('Running'), world)
            self.move_counter += 1

            self.change_direction = False
            if self.move_counter > (self.move_radius * Display.TILE_DIMENSION_X) / self.x_vel or self.wall_collision:
                self.change_direction = True
                self.set_idling(world)
                self.wall_collision = False
            # self.health_rect.x += scroll

    def set_idling(self, world):
        self.idling = True
        self.idling_counter = 50
        self.update_action(self.get_index('Idle'), world)

    def draw(self, surface, target):  # custom draw method for enemy class
        debug = 0
        temp = self.rect.copy()
        temp.x = temp.x - target.rect.x + Display.WIDTH // 2
        temp.y = temp.y - target.rect.y + Display.HEIGHT // 2

        surface.blit(pygame.transform.flip(self.image, self.flip_image or self.direction == -1, False), temp)
        if debug:
            pygame.draw.rect(surface, (255, 0, 0), self.attack_vision, 2)
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2)
        self.draw_health_bar(surface, target)

    def update(self, player, surface, world):
        self.animation_handling()
        # pygame.draw.rect(Display.screen, (255, 0, 0), enemy.attack_vision,2)
        if self.health > 0:
            self.trigger = False
            if self.start_attack(player, world):  # check if player collision has occurred
                pass
            player.sword_collision(self)
            self.sword_collision(player)  # check for collision with the player
        elif self.remove:
            self.trigger = True

        self.AI(world, player)  # do enemy AI

    def regen(self):
        self.health = self.max_health
        self.update_action(self.get_index('Idle'))


class Group(pygame.sprite.Group):
    def __init__(self, *args):
        super().__init__()
        self.add(*args)

    # this is for images
    def draw(self, surface, scroll=0, target=None):
        for sprite in self.sprites():
            # Check if the sprite has a `draw` method.
            if hasattr(sprite, 'draw'):
                sprite.draw(surface, target=target)
            else:
                surface.blit(sprite.image, sprite.rect)

    def regen(self):
        for sprite in self.sprites():
            # Check if the sprite has a `regen` method.
            if hasattr(sprite, 'regen'):
                sprite.regen()

    def check_death(self):
        ask_question = False
        for obj in self.sprites():
            if obj.trigger:
                obj.kill()
                ask_question = True
        return ask_question


class BoxGroup:
    def __init__(self, *args):
        self.objects = [*args]

    def update_boxes(self, surface):
        obj = False
        for box in self.objects:
            if hasattr(box, 'show'):
                box.show(surface)
            if hasattr(box, 'check_hover'):
                box.check_hover()
            if hasattr(box, 'check_click') and not obj:  # if a box hasn't already been clicked
                if box.check_click():
                    obj = box
        return obj

    def set_background(self, color):
        pass

    def check_clicks(self):
        obj = False
        for box in self.objects:
            if hasattr(box, 'check_click') and not obj:
                if box.check_click():
                    obj = box
        return obj

    def get_list(self):
        return self.objects
