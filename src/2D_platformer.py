import pygame
import os
from win32api import GetSystemMetrics
from math import floor

screen_w = GetSystemMetrics(0)
screen_h = GetSystemMetrics(1)

pygame.init()

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)
screen = pygame.display.set_mode((screen_w, screen_h))
width, height = pygame.display.get_surface().get_size()

pygame.display.set_caption("Test Classes")
#icon = pygame.image.load("icon.png")
#pygame.display.set_icon(icon)

clock = pygame.time.Clock()

#TODO see how to make an infinite number of instances of a class
#TODO make NPCs
#TODO make faraway sprites disappear
#todo make enemy AI (it's basic: walks, falls, hits walls)

#Creating groups
class group_class(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
    def move(self, x, y):
        for sprite in self:
            sprite.rect.x -= x * player.speed
            sprite.rect.y += y

platform_group = group_class()
enemy_group = group_class()
not_player_group = group_class()
all_group = group_class()

class player_class(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, all_group)
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = screen_w // 2 - self.image.get_width() // 2
        self.rect.y = screen_h // 2 + 100
        self.mask = pygame.mask.from_surface(self.image)
        self.walking = False
        self.speed = 2
        self.velocity = 2.2
        self.mass = 2
        self.jumping = False
        self.double_jump = False
        self.double_jump_count = 0
        self.wall_jumping = [False, 0]
        self.dashing = False
        self.dash_count = 0
        self.dash_speed = 10
        self.dash_i = 0
        self.facing = "right"
        self.touching_wall = "none"
        self.looking = "none"
        self.look_i = 0

    def walk(self, x):
        #Player touching a wall?
        if pygame.sprite.collide_mask(player, ground) is not None:
            if pygame.sprite.collide_mask(player, ground)[1] < 55 and pygame.sprite.collide_mask(player, ground)[0] == 0:
                    self.touching_wall = "left"
            elif pygame.sprite.collide_mask(player, ground)[1] >= 58 and player.mask.overlap_area(ground.mask, (ground.rect.x - player.rect.x, ground.rect.y - player.rect.y)) > 384:
                self.touching_wall = "right"
            elif self.jumping and pygame.sprite.collide_mask(player, ground)[1] < 59 and pygame.sprite.collide_mask(player, ground)[0] >= 60:
                self.touching_wall = "right"
        else:
            self.touching_wall = "none"
        #Get player direction
        if x > 0:
            self.facing = "right"
        else:
            self.facing = "left"
        #Walk if not touching wall
        if self.touching_wall == "none":
            not_player_group.move(x, 0)
        #To walk away from walls
        if self.touching_wall == "left" and self.facing == "right":
            not_player_group.move(x, 0)
            self.touching_wall = "none"
        if self.touching_wall == "right" and self.facing == "left":
            not_player_group.move(x, 0)
            self.touching_wall = "none"
        #To fall off platforms
        if not self.jumping:
            if pygame.sprite.collide_mask(player, ground) is None:
                self.jumping = True
                self.velocity = -1

    def jump(self):
        #Math for jumping physics
        if self.velocity >= 0:
            not_player_group.move(0, int(round((0.5 * player.mass * (player.velocity ** 2)))))
        else:
            not_player_group.move(0, -1 * int(round((0.5 * player.mass * (player.velocity ** 2)))))
        self.velocity -= 0.01
        #Go down faster
        if floor(self.velocity) == 0:
            self.velocity = -1
        #Max downwards velocity
        if self.velocity <= -2.2:
            self.velocity += 0.01
        #For double Jump
        if self.double_jump and player.double_jump_count <= 1:
            self.velocity = 2.2
            self.double_jump = False
            self.double_jump_count += 1
        #To land on ground
        if pygame.sprite.collide_mask(player, ground) is not None:
            if pygame.sprite.collide_mask(player, ground)[1] >= 58:
                self.jumping = False
                self.wall_jumping = [False, 0]
                self.velocity = 2.2
        #To hit the underside of platforms
        if pygame.sprite.collide_mask(player, ground) is not None:
            if pygame.sprite.collide_mask(player, ground)[1] <= 4:
                self.jumping = True
                self.velocity = -1
        #To not go through the ground when sliding on walls
        if self.touching_wall == "left":
            if player.mask.overlap_area(ground.mask, (ground.rect.x - player.rect.x, ground.rect.y - player.rect.y)) > 128:
                self.jumping = False
                self.velocity = 2.2

    def wall_jump(self, direction):
        self.jumping = True
        if not self.walking:
            self.walk(direction)
        if self.walking or self.touching_wall != "none":
            self.wall_jumping = [False, 0]

    def dash(self):
        self.dash_i += 1
        if self.facing == "right":
            not_player_group.move(self.dash_speed, 0)
        else:
            not_player_group.move(self.dash_speed*-1, 0)
        #To not go into walls
        if player.mask.overlap_area(ground.mask, (ground.rect.x - player.rect.x, ground.rect.y - player.rect.y)) > 384:
            self.dashing = False
            if self.facing == "right":
                not_player_group.move(self.dash_speed*-1, 0)
            if self.facing == "left":
                not_player_group.move(self.dash_speed, 0)
            self.dash_i = 0
            self.dash_count += 1
        # To fall off platforms
        if not self.jumping:
            if pygame.sprite.collide_mask(player, ground) is None:
                self.jumping = True
                self.velocity = -1
        #To stop dash
        if self.dash_i > 20:
            self.dashing = False
            self.dash_i = 0
            self.dash_count += 1

    def look(self, direction):
        #To look up or down
        if self.looking == "none":
            all_group.move(0, 4 * direction)
            self.look_i += direction
        #To go back to normal after key is up
        elif self.looking == "up" and not activeKey[pygame.K_w] or self.looking == "down" and not activeKey[pygame.K_s]:
            all_group.move(0, 4 * direction)
            self.look_i += direction
        elif self.looking == "none" and not activeKey[pygame.K_w] or self.looking == "none" and not activeKey[pygame.K_s]:
            all_group.move(0, 4 * direction)
            self.look_i += direction
        #To stop at the right distance
        if self.look_i > 60:
            self.looking = "up"
        elif self.look_i < -60:
            self.looking = "down"
        elif self.look_i == 0:
            self.looking = "none"

class platform_class(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, platform_group, not_player_group, all_group)
        self.image = pygame.image.load("ground4.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = screen_w // 2 - self.image.get_width() // 2
        self.rect.y = screen_h // 2 + player_class().image.get_height() + 100
        self.mask = pygame.mask.from_surface(self.image)

class enemy_class(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, enemy_group, not_player_group, all_group)
        self.image = pygame.image.load("enemy.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = screen_h // 2 + 100
        self.mask = pygame.mask.from_surface(self.image)
        self.velocity = 2.2
        self.mass = 2
        self.jumping = False
        self.facing = "right"
        self.touching_wall = "none"
    def walk(self, x):
        #Enemy touching a wall?
        if pygame.sprite.collide_mask(self, ground) is not None:
            if pygame.sprite.collide_mask(self, ground)[1] < 55 and pygame.sprite.collide_mask(self, ground)[0] == 0:
                self.touching_wall = "left"
            elif pygame.sprite.collide_mask(self, ground)[1] >= 58 and self.mask.overlap_area(ground.mask, (ground.rect.x - self.rect.x, ground.rect.y - self.rect.y)) > 384:
                self.touching_wall = "right"
            elif self.jumping and pygame.sprite.collide_mask(self, ground)[1] < 59 and \
                    pygame.sprite.collide_mask(self, ground)[0] >= 60:
                self.touching_wall = "right"
        else:
            self.touching_wall = "none"
        #Get enemy direction
        if x > 0:
            self.facing = "right"
        if x < 0:
            self.facing = "left"
        #Walk if not touching wall
        if self.touching_wall == "none":
            self.rect.x += x
        #To walk away from walls
        if self.touching_wall == "left" and self.facing == "right":
            self.rect.x += x
            self.touching_wall = "none"
        if self.touching_wall == "right" and self.facing == "left":
            self.rect.x += x
            self.touching_wall = "none"
        #To fall off platforms
        if not self.jumping:
            if pygame.sprite.collide_mask(self, ground) is None:
                self.jumping = True
                self.velocity = -1
    def jump(self):
        #Math for jumping physics
        if self.velocity <= 0:
            enemy_group.move(0, int(round((0.5 * self.mass * (self.velocity ** 2)))))
        else:
            enemy_group.move(0, -1 * int(round((0.5 * self.mass * (self.velocity ** 2)))))
        self.velocity -= 0.01
        #Go down faster
        if floor(self.velocity) == 0:
            self.velocity = -1
        #Max downwards velocity
        if self.velocity <= -2.2:
            self.velocity += 0.01
        # To land on ground
        if pygame.sprite.collide_mask(self, ground) is not None:
            if pygame.sprite.collide_mask(self, ground)[1] >= 58:
                self.jumping = False
                self.velocity = 2.2
        # To hit the underside of platforms
        if pygame.sprite.collide_mask(self, ground) is not None:
            if pygame.sprite.collide_mask(self, ground)[1] <= 4:
                self.jumping = True
                self.velocity = -1

#Creating Sprites
player = player_class()
ground = platform_class()
enemy = enemy_class()

running = True
while running:
    screen.fill((0, 0, 0))

#Limit and show fps
    clock.tick(450)
    font = pygame.font.Font("AnotherFlight.ttf", 50)
    text = font.render(str(round(clock.get_fps())), True, (250, 250, 250))
    screen.blit(text, (20, 20))

#Get pressed key
    activeKey = pygame.key.get_pressed()

#Player movement
    #Right
    if activeKey[pygame.K_d]:
        player.walk(1)
        player.walking = True
    #Left
    if activeKey[pygame.K_a]:
        player.walk(-1)
        player.walking = True
    if not activeKey[pygame.K_d] and not activeKey[pygame.K_a]:
        player.walking = False
    #Wall Jump
    if player.wall_jumping[0]:
        player.wall_jump(player.wall_jumping[1])
    #Jump
    if player.jumping:
        player.jump()
    if not player.jumping:
        player.double_jump_count = 0
    #Dash
    if player.dashing:
        player.dash()
    if not player.jumping and player.dash_count > 0:
        player.dash_count = 0

    # Input to look around
    #  Look up
    if activeKey[pygame.K_w] and not activeKey[pygame.K_s]:
        player.look(1)
    #  Look down
    if activeKey[pygame.K_s] and not activeKey[pygame.K_w]:
        player.look(-1)
    #  Look back down when looking up
    if not activeKey[pygame.K_w]:
        if player.look_i > 0:
            player.look(-1)
    #  Look back up when looking down
    if not activeKey[pygame.K_s]:
        if player.look_i < 0:
            player.look(1)

    if player.rect.x > enemy.rect.x:
        enemy.walk(1)
    if player.rect.x < enemy.rect.x:
        enemy.walk(-1)
    if enemy.jumping:
        enemy.jump()

#Show images on screen
    screen.blit(player.image, player.rect)
    screen.blit(ground.image, ground.rect)
    screen.blit(enemy.image, enemy.rect)

    for event in pygame.event.get():
        # Listen for inputs
        if event.type == pygame.KEYDOWN:
            # Input to jump
            if event.key == pygame.K_SPACE:
                if not player.jumping:
                    player.jumping = True
                #Input to wall jump
                if player.touching_wall != "none":
                    if player.touching_wall == "right":
                        player.velocity = 2.2
                        player.jumping = False
                        player.wall_jumping = [True, -1]
                    if player.touching_wall == "left":
                        player.velocity = 2.2
                        player.jumping = False
                        player.wall_jumping = [True, 1]
                #Input to double jump
                else:
                    if player.jumping and not player.double_jump:
                        player.double_jump = True
            #Input to dash
            if event.key == pygame.K_LSHIFT:
                if not player.dashing and player.dash_count < 1:
                    player.dashing = True

        #To quit
        if event.type == pygame.QUIT:
            quit()

    pygame.display.update()
