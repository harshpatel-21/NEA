import pygame, sys, os

x = '\\'.join(os.path.abspath(__file__).split('\\')[:-2])  # allow imports from main folder
sys.path.insert(1, x)

from WINDOW import Display as window

# websites:
# https://www.piskelapp.com/
# https://pixlr.com/x/#home

pygame.init()
GRAVITY = 0.75


class Arrow(pygame.sprite.Sprite):
    def __init__(self, shooter):
        pygame.sprite.Sprite.__init__(self)
        self.shooter = shooter
        self.image = pygame.image.load('images/Arrow04.png').convert_alpha()
        self.image = pygame.transform.flip(self.image, shooter.direction == -1, False)
        self.rect = self.image.get_rect()
        self.rect.topleft = (shooter.rect.x, shooter.rect.y)
        self.direction = shooter.direction

        if self.direction == 1:  # adjusting starting position of arrow
            self.rect.x += shooter.rect.w
        else:
            self.rect.x -= self.rect.w

        self.rect.y = shooter.rect.y + 32
        self.x_vel = 18
        self.acceleration = 2.5
        self.mask = pygame.mask.from_surface(self.image)
        self.remove = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self):
        self.rect.x += (self.x_vel * self.acceleration) * self.direction
        # self.acceleration -= 0.035*self.acceleration
        self.acceleration *= 0.9

        if (self.rect.left > window.WIDTH) or (self.rect.right < 0) or self.acceleration < 0.08:
            self.remove = True  # set the flag to remove the arrow to true

    def check_collision(self, obj):  # checking for arrow collision from bow_attack
        # flip the mask of the image during collision detection
        obj_mask = pygame.mask.from_surface(pygame.transform.flip(obj.image, obj.direction == -1, False))
        offset_x = obj.rect.x - self.rect.x
        offset_y = obj.rect.y - self.rect.y
        collision = self.mask.overlap(obj_mask, (offset_x, offset_y))

        # change border color if collision with arrow has occurred
        if collision:
            obj.border_color = (0, 255, 0)
        else:
            obj.border_color = (255, 0, 0)
        return collision


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, entity_type, scale, max_health=100, speed=5, all_animations=None):
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
        self.speed = speed
        self.direction = 1  # [1,-1] = [facing right, facing left]
        self.flip_image = False
        self.jumping = False
        self.in_air = True
        self.sword_attack = False
        self.bow_attack = False
        self.current_weapon = 2  # 1 == sword, 2 == Bow
        self.shoot_cooldown = 10
        self.shoot_cooldown_timer = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.combat_animations = [4, 5]
        self.border_color = (255, 0, 0)
        self.collisions = 0
        bow_dps = 20
        sword_dps = 50
        self.health2 = self.health
        self.difference = self.health - self.health2
        self.current_weapon_damage = {1: sword_dps, 2: bow_dps}  # sword deals 50 damage, bow deals 20
        self.increase_health = 0

    def move(self, moving_left, moving_right):  # handle player movement
        # reset movement variables
        dx = dy = 0

        if not self.check_alive():
            return
        # horizontal movement
        if self.bow_attack:  # don't allow movement during an attack animation
            return

        if moving_left:
            dx = -self.speed
            self.flip_image = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip_image = False
            self.direction = 1

        # jumping/vertical movement
        if self.jumping and (not self.in_air):
            self.y_vel = -15
            self.jumping = False
            self.in_air = True

        # gravity
        self.y_vel = min(self.y_vel + GRAVITY, 10)
        dy += self.y_vel

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom  # add the remaining distance between floor and player
            self.in_air = False

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
                          max(2, full_x * (min(self.max_health, self.health + self.difference) / self.max_health)),
                          full_y)
        border = pygame.Rect(health_x, health_y, full_x, full_y)

        if self.increase_health:  # if the health is increasing
            self.difference = min(self.increase_health,(self.difference + health_bar_dx))  # increase health bar gradually
            if self.difference >= self.increase_health:
                self.increase_health = 0
        else:
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
        shoot_projectile = False
        # update entity image
        self.image = self.animations[self.current_action][self.animation_pointer]
        image_rect = self.image.get_rect()
        image_rect.bottomleft = self.rect.bottomleft
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
                'Running2': (scale[0] * 1.4, scale[1])
            },
            'player2': {
                'Idle': (scale[0] * 1, scale[1] * 1.15),
                'Die': (scale[0] * 1, scale[1] * 0.95),
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

            temp += [pygame.transform.scale(pygame.image.load(f'images/{entity_type}/{animation}/{images[i]}'), scale2)]
        self.animations += [temp]

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip_image or self.direction == -1, False), self.rect)
        # pygame.draw.rect(surface,self.border_color,self.rect,2)

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


class Enemy(Entity):
    def __init__(self, *args, **kwargs):
        arguments = [args]
        keywords = [kwargs]
        # print(arguments, keywords)
        super().__init__(*args, **kwargs)

    def check_collision(self, obj):  # check for sword attack collision
        if not self.check_alive():
            return
        obj_mask = pygame.mask.from_surface(pygame.transform.flip(obj.image, obj.direction == -1,
                                                                  False))  # flips the mask of the image during collision detection
        offset_x = obj.rect.x - self.rect.x
        offset_y = obj.rect.y - self.rect.y
        current_mask = pygame.mask.from_surface(pygame.transform.flip(self.image, self.direction == -1,
                                                                      False))  # flips the mask of the image during collision detection
        collision = current_mask.overlap(obj_mask, (
            offset_x, offset_y)) and obj.sword_attack  # making sure player is in sword animation
        if collision:
            self.collisions += 1
        else:  # if no there is no longer any collision
            if self.collisions:  # if there were collisions recorded prior
                # print(obj.current_weapon, obj.current_weapon_damage.get(obj.current_weapon))
                self.health2 = self.health
                self.health -= obj.current_weapon_damage.get(
                    obj.current_weapon)  # subtract health based on weapon equipped
                self.difference = max(0, self.health2 - self.health)
            # print(self.health)
            self.collisions = 0  # reset the collisions counter
        return x
