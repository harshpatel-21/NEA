import pygame, sys, os, random, inspect

x = '\\'.join(os.path.abspath(__file__).split('\\')[:-2])  # allow imports from main folder
sys.path.insert(1, x)

from WINDOW import Display

# websites:
# https://www.piskelapp.com/
# https://pixlr.com/x/#home

pygame.init()
GRAVITY = 0.75


class Arrow(pygame.sprite.Sprite):
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
        self.x_vel = 18
        self.acceleration = 2.5
        self.mask = pygame.mask.from_surface(self.image)
        self.remove = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, surface, world, enemy_group, player, arr=None):
        self.draw(surface)  # draw the arrow onto the screen
        self.check_collision(enemy_group)  # check for collision with enemies
        self.check_collision(player)  # check for collision with player

        if not self.remove: self.rect.x += (self.x_vel * self.acceleration) * self.direction
        # self.acceleration -= 0.035*self.acceleration
        self.acceleration *= 0.9

        # check if the arrow has gone off the screen or low acceleration
        if (self.rect.left > Display.WIDTH) or (self.rect.right < 0) or self.acceleration < 0.08:
            self.remove = True  # set the flag to remove the arrow to true
            # self.direction *= -1

        # check for tile collision
        # for

        if self.remove:
            # arr.remove(self) # used when arrows were stored in an array
            self.kill() # frees up memory and removes all instances of this specific arrow from associated groups

    def check_collision(self, objs):  # checking for arrow collision from bow_attack
        # flip the mask of the image during collision detection
        if isinstance(objs, Group):
            for obj in objs:
                if self.mask_collision(obj):
                    self.remove = True
        else:
            if self.mask_collision(objs):
                self.remove = True

    def mask_collision(self, obj):
        if hasattr(obj, 'check_alive'):
            if not obj.check_alive(): return

        obj_mask = pygame.mask.from_surface(pygame.transform.flip(obj.image, obj.direction == -1, False))
        offset_x = obj.rect.x - self.rect.x
        offset_y = obj.rect.y - self.rect.y
        collision = self.mask.overlap(obj_mask, (offset_x, offset_y))

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

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, entity_type, scale, max_health=1000, x_vel=5, all_animations=None, bow_dps=20,
                 sword_dps=40):
        self.all_animations = all_animations
        if all_animations is None and entity_type == 'player':
            self.all_animations = ['Idle2', 'Running2', 'Jumping', 'Falling', 'Sword', 'Bow', 'Die']
        pygame.sprite.Sprite.__init__(self)
        self.max_health = max_health
        self.health = self.max_health
        self.y_vel = 0
        self.entity_type = entity_type
        self.animations = []
        self.animation_pointer = 0
        self.current_action = 0
        self.time1 = pygame.time.get_ticks()
        for animation in self.all_animations:
            self.get_animations(entity_type, animation, scale)
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
        self.combat_animations = [4, 5]
        self.border_color = (255, 0, 0)
        self.collisions = 0
        self.health2 = self.health
        self.difference = self.health - self.health2
        self.current_weapon_damage = {1: sword_dps, 2: bow_dps}  # sword deals 50 damage, bow deals 20
        self.increase_health = 0

    def move(self, moving_left, moving_right, world):  # handle player movement
        # reset movement variables
        dx = dy = 0

        if not self.check_alive():
            return
        # horizontal movement
        if self.bow_attack:  # don't allow movement during an attack animation
            return

        if moving_left:
            dx = -self.x_vel
            self.flip_image = True
            self.direction = -1

        if moving_right:
            dx = self.x_vel
            self.flip_image = False
            self.direction = 1

        # jumping/vertical movement
        if self.jumping and (not self.in_air):
            self.y_vel = -13
            self.jumping = False
            self.in_air = True

        # gravity
        self.y_vel = min(self.y_vel + GRAVITY, 10)
        dy += self.y_vel

        # check collision with floor
        for tile in world.obstacle_list:
            # check collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.w, self.rect.h):
                dx = 0

            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.w, self.rect.h):
                dy = 0
                # check if jumping and below ground
                if self.y_vel < 0:
                    self.y_vel = 0
                    # tile[1].bottom = self.rect.top
                    # self.rect.top = tile[1].bottom

                elif self.y_vel >= 0:
                    self.y_vel = 0
                    self.in_air = False
                    # tile[1].top = self.rect.bottom
                    self.rect.bottom = tile[1].top
        # if self.rect.bottom + dy > 300:
        #     dy = 300 - self.rect.bottom  # add the remaining distance between floor and player
        #     self.in_air = False

        # update player position
        self.rect.x += dx
        self.rect.y += dy

    # noinspection PyTypeChecker
    def draw_health_bar(self, surface):
        health_bar_dx = 4 * [-1, 1][self.increase_health > 0]
        x_padding = {
            'player': 10,
            'player2': 13
        }
        y_padding = 11
        full_x = 70
        full_y = 6
        temp_surface = pygame.Surface((full_x, full_y))
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2) # draw a border around the entity
        health_x, health_y = self.rect.x, self.rect.top - y_padding

        if self.direction == 1:
            entity_x = self.rect.left
        else:
            health_x = self.rect.right - full_x
        health_x += x_padding[self.entity_type] * self.direction

        initial = pygame.Rect(health_x, health_y, full_x, full_y)
        new = pygame.Rect(health_x, health_y,
                          max(2, full_x * (min(self.max_health, self.health) / self.max_health)),
                          full_y)
        border = pygame.Rect(health_x, health_y, full_x, full_y)

        self.difference = max(0, self.difference + health_bar_dx)  # decrease health bar gradually

        if self.health <= 0 and self.difference == 0:  # if the player is dead then don't draw the player
            return

        else:
            pygame.draw.rect(surface, (255, 0, 0), initial)
            pygame.draw.rect(surface, (0, 255, 0), new)
            pygame.draw.rect(surface, (0, 0, 0), border, 2)

    # self.difference += health_bar_dx

    def animation_handling(self):  # updates the animation frame
        self.check_alive()
        self.shoot_cooldown_timer = max(0, self.shoot_cooldown_timer - 1)  # makes sure the cooldown doesn't go below 0
        # update animation based on a timer since last time recorded
        cooldown_time = 120  # every 120 main game loops change animation frame
        if self.current_action in self.combat_animations:
            cooldown_time = 90
        # if self.current_action == 4 and self.entity_type == 'player':
        #     cooldown_time = 60
        if self.current_action == 2 and self.entity_type == 'player2':
            cooldown_time = 90
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
        hurt_index = self.get_index('Hurt')
        if (current_time - self.time1) > cooldown_time:
            self.animation_pointer += 1  # add one to animation pointer
            if self.current_action in self.combat_animations:  # if its a combat animation
                if self.animation_pointer >= len(
                        self.animations[self.current_action]):  # if at the last frame of animation
                    self.animation_pointer = 0  # reset animation pointer
                    self.current_action = 0  # go back to idle position
                    self.sword_attack = False  # no longer attacking with a weapon
                    if self.bow_attack:  # if currently in bow animation, set finished bow_animation to True
                        self.shoot_cooldown_timer = self.shoot_cooldown
                        shoot_projectile = True
                    self.bow_attack = False  # no longer attacking with a weapon

            elif self.current_action == death_index:  # death animation
                self.animation_pointer = min(len(self.animations[death_index]) - 1, self.animation_pointer)

            else:  # looping animations
                self.animation_pointer = self.animation_pointer % len(self.animations[self.current_action])

            self.time1 = pygame.time.get_ticks()

        if shoot_projectile:
            arrow = self.shoot()
            if arrow:
                return arrow

    def shoot(self):
        return Arrow(self)  # return an Arrow object

    def update_action(self, new_action):
        # check if the new action is different to the new action
        # if the new action is the same as the old action, it would set animation pointer to 0 every time so only the
        # first frame of the animation would be shown. By adding this check, it makes it so that the animation pointer and animation is changed/reset
        # only if there is a change in the player action.
        if new_action != self.current_action:
            self.current_action = new_action
            # reset the index at which the animation for the specific action starts at
            self.animation_pointer = 0
            self.time1 = pygame.time.get_ticks()

    def get_animations(self, entity_type, animation, scale):  # add animations for this sprite into a list
        animation_scale = {
            'player': {
                'Bow': (scale[0] * 1.6, scale[1]),
                'Sword': (scale[0] * 1.4, scale[1]),
                'Idle3': (scale[0] * 5, scale[1]),
                'Idle2': (scale[0] * 1.4, scale[1]),
                'Die': (scale[0] * 1, scale[1] * 0.8),
                'Running2': (scale[0] * 1.4, scale[1]),
                'Jumping': (scale[0]*1.4, scale[1]),
                'Falling': (scale[0]*1.4, scale[1])
            },
            'player2': {
                'Idle': (scale[0] * 0.5, scale[1] * 1),
                'Die': (scale[0] * 1.2, scale[1] * 0.95),
                'Run': (scale[0] * 0.5, scale[1]),
                'Attack': (scale[0] * 1.2, scale[1])
            }
        }
        temp = []
        images = os.listdir(f'images/{entity_type}/{animation}')  # get a list of the image names for the animation
        scale2 = scale
        for i in range(len(images)):
            scale_info = animation_scale.get(entity_type)
            if scale_info:
                scale_data = scale_info.get(animation)
                if scale_data: scale2 = [*map(int, scale_data)]
            scale2 = [*map(int,(scale2[0]*0.8,scale2[1]*0.8))]
            temp += [pygame.transform.scale(pygame.image.load(f'images/{entity_type}/{animation}/{images[i]}'), scale2)]
        self.animations += [temp]

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip_image or self.direction == -1, False), self.rect)
        # pygame.draw.rect(surface,self.border_color, self.rect, 2)

        self.draw_health_bar(surface)

    # pygame.draw.rect(surface,self.border_color,self.rect,2)

    def check_alive(self):  # check if the entity is alive
        if self.health <= 0:  # if they've died
            self.health = 0  # health is back at 0
            x = self.get_index('Die')  # get the index of where the 'Die' animation is
            self.update_action(x)  # update the series of images that contain the death animation
        return self.health > 0

    def get_index(self, animation):  # get the death index from the list of animations
        index = 0
        if animation in self.all_animations:
            index = self.all_animations.index(animation)
        return index

    def sword_collision(self, obj):  # check for sword attack collision
        if self.check_collision(obj) and obj.sword_attack:
            self.collisions += 1 and obj.sword_attack and self.direction != obj.direction
            self.health -= obj.current_weapon_damage.get(
                obj.current_weapon) / 25
        # else:  # if no there is no longer any collision
        #     if self.collisions == 1000:  # if there were collisions recorded prior
        #         # print(obj.current_weapon, obj.current_weapon_damage.get(obj.current_weapon))
        #         self.health2 = self.health
        #         self.health -= obj.current_weapon_damage.get(
        #             obj.current_weapon)  # subtract health based on weapon equipped
        #         self.difference = max(0, self.health2 - self.health)
        #     # print(self.health)
        #     self.collisions = 0  # reset the collisions counter
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
    def __init__(self, x, y, entity_type, scale, max_health=100, x_vel=5, all_animations=None, attack_radius=150):
        super().__init__(x, y, entity_type, scale, max_health, x_vel, all_animations)
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.attack_vision = pygame.Rect(0, 0, attack_radius, 20)
        self.combat_animations = [3]
        self.attacked = False
        self.wait = 0
        self.change_direction = False

    def rec_collision(self, obj):
        return self.attack_vision.colliderect(obj.rect)

    def start_attack(self, obj):
        if self.wait == 0 and self.rec_collision(obj):
            self.sword_attack = True
            self.update_action(3)  # change the animation to attack animation
            self.wait = 100
            return True
        return False

    def AI(self, world):
        if self.in_air:  # if the enemy is falling
            self.move(0, 0, world)  # don't move in any direction
            return  # don't do anything else related to AI movement
        self.wait = max(0, self.wait - 1)

        AI_moving_right = False
        if self.sword_attack:
            return

        self.attack_vision.center = self.rect.center
        if self.direction == 1:
            self.attack_vision.left = self.rect.right
        else:
            self.attack_vision.right = self.rect.left

        if self.alive:
            # checking if enemy is not already idling and not falling/jumping
            if random.randint(1, 500) == 1 and not self.idling and not self.in_air:
                self.set_idling()
                pass

            #if the enemy is in idling motion:
            if self.idling:
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False
                    if self.change_direction:
                        self.direction *= -1
                        self.move_counter *= -1
                return  # don't attempt to move the player in idling animation

            if self.direction == 1:
                AI_moving_right = True

            AI_moving_left = not AI_moving_right
            self.move(AI_moving_left, AI_moving_right, world)
            self.update_action(2)
            self.move_counter += 1

            self.change_direction = False
            if self.move_counter > Display.TILE_DIMENSION_X:
                self.change_direction = True
                self.set_idling()

    def set_idling(self):
        self.idling = True
        self.idling_counter = 50
        self.update_action(0)

    def draw(self, surface): # custom draw method for enemy class
        debug = 0
        surface.blit(pygame.transform.flip(self.image, self.flip_image or self.direction == -1, False), self.rect)
        if debug:
            pygame.draw.rect(surface, (255, 0, 0), self.attack_vision, 2)
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2)
        self.draw_health_bar(surface)

    def update(self, player, surface, world):
        self.animation_handling()
        # pygame.draw.rect(Display.screen, (255, 0, 0), enemy.attack_vision,2)
        if self.health <= 0:
            # if enemy.difference <= 0:
            #     enemy.kill() # free memory space
            #     enemies.remove(enemy)
            return  # if the enemy has died, they don't need to check for collision or do movement

        self.start_attack(player) # check if player collision has occurred
        player.sword_collision(self)
        self.sword_collision(player)  # check for collision with the player
        self.AI(world) # do enemy AI

    def regen(self):
        self.health = self.max_health
        self.update_action(0)

class Group(pygame.sprite.Group):
    def __init__(self, *args):
        super().__init__()
        self.add(*args)

    def draw(self, surface):
        for sprite in self.sprites():
            # Check if the sprite has a `draw` method.
            if hasattr(sprite, 'draw'):
                sprite.draw(surface)
            else:
                surface.blit(sprite.image, sprite.rect)

    def regen(self):
        for sprite in self.sprites():
            # Check if the sprite has a `regen` method.
            if hasattr(sprite, 'regen'):
                sprite.regen()

