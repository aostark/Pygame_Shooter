import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()

SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

# frame rate
clock = pygame.time.Clock()
FPS = 60

# define game variables
gravity = 0.70
scroll_threshold = 200
rows = 16
columns = 150
tile_size = SCREEN_WIDTH // 30
tile_types = 21
screen_scroll = 0
bg_scroll = 0
level = 1
max_levels = 3
start_game = False
start_intro = False

# load images
# button images
start_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\start_btn.png').convert_alpha()
exit_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\exit_btn.png').convert_alpha()
restart_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\restart_btn.png').convert_alpha()
# background images
pine1_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\Background\pine1.png').convert_alpha()
pine2_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\Background\pine2.png').convert_alpha()
mountain_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\Background\mountain.png').convert_alpha()
sky_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\Background\sky_cloud.png').convert_alpha()
# store tiles in a list
img_list = []
for x in range(tile_types):
    img = pygame.image.load(f"img/Tile/{x}.png")
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)
bullet_img = pygame.image.load(
    r'D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\icons\bullet.png').convert_alpha()
grenade_img = pygame.image.load(
    r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\icons\grenade.png").convert_alpha()
# pick up boxes
health_box_img = pygame.image.load(
    r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\icons\health_box.png").convert_alpha()
ammo_box_img = pygame.image.load(
    r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\icons\ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load(
    r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\icons\grenade_box.png").convert_alpha()

item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img
}

# Player actions
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# load music and sounds
pygame.mixer.music.load(r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\audio\music2.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound(r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\audio\jump.wav")
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound(r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\audio\shot.wav")
shot_fx.set_volume(0.04)
grenade_fx = pygame.mixer.Sound(r"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\audio\grenade.wav")
grenade_fx.set_volume(0.1)

# define colors
bg_color = (255, 218, 185)
red = (255, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
black = (0, 0, 0)

font = pygame.font.SysFont("Chiller", 28)


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_background():
    screen.fill(bg_color)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


# reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(rows):
        r = [-1] * columns
        data.append(r)
    return data


# To draw the player + player images
class Soldier(pygame.sprite.Sprite):
    def __init__(self, character_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.character_type = character_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # AI specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # This part is responsible for animating images
        # load all images for the players
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(fr"img\{self.character_type}\{animation}"))
            for i in range(num_of_frames):
                image = pygame.image.load(fr"img\{self.character_type}\{animation}\{i}.png").convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset moving variables
        screen_scroll = 0
        delta_x = 0
        delta_y = 0

        if moving_left:
            delta_x = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            delta_x = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.velocity_y = -12
            self.jump = False
            self.in_air = True

        # apply gravity
        self.velocity_y += gravity
        if self.velocity_y > 10:
            self.velocity_y
        delta_y += self.velocity_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.width, self.height):
                delta_x = 0
                # if the AI has hit the wall, make it turn around
                if self.character_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):
                # check if below the ground (jumping)
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    delta_y = tile[1].bottom - self.rect.top
                # check if above the ground (falling)
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    self.in_air = False
                    delta_y = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off the edges of the screen
        if self.character_type == "player":
            if self.rect.left + delta_x < 0 or self.rect.right + delta_x > SCREEN_WIDTH:
                delta_x = 0

        # update rectangle position (player/enemy position)
        self.rect.x += delta_x
        self.rect.y += delta_y

        # update scroll based on player position
        if self.character_type == "player":
            if (self.rect.right > SCREEN_WIDTH - scroll_threshold and bg_scroll < (
                    world.level_length * tile_size) - SCREEN_WIDTH) or (
                    self.rect.left < scroll_threshold and bg_scroll > abs(delta_x)):
                self.rect.x -= delta_x
                screen_scroll = -delta_x
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 10
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0 means Idle
                self.idling = True
                self.idling_counter = 50
            # check if the AI is near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # 0 means Idle
                # shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1 means Run
                    self.move_counter += 1
                    # update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > tile_size:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        animation_cooldown = 130
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()  # resets the timer
            self.frame_index += 1
        #  if the animation has run out, reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animations settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile <= 10:
                        water = Water(img, x * tile_size, y * tile_size)
                        water_group.add(water)
                    elif 11 <= tile <= 14:
                        decoration = Decoration(img, x * tile_size, y * tile_size)
                        decoration_group.add(decoration)
                    elif tile == 15:  # create player
                        player = Soldier('player', x * tile_size, y * tile_size, 1.75, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # create enemies
                        enemy = Soldier('enemy', x * tile_size, y * tile_size, 1.75, 3, 20, 1)
                        enemy_group.add(enemy)
                    elif tile == 17:  # create ammo box
                        item_box = ItemBox('Ammo', x * tile_size, y * tile_size)
                        item_box_group.add(item_box)
                    elif tile == 18:  # create grenade box
                        item_box = ItemBox('Grenade', x * tile_size, y * tile_size)
                        item_box_group.add(item_box)
                    elif tile == 19:  # create health box
                        item_box = ItemBox('Health', x * tile_size, y * tile_size)
                        item_box_group.add(item_box)
                    elif tile == 20:  # create exit
                        exit = Exit(img, x * tile_size, y * tile_size)
                        exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # check if the player picked up a box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == "Health":
                player.health += 25
                if player.health >= player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 15
            else:
                player.grenades += 3
            # delete the item box
            self.kill()


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, black, (self.x - 1, self.y - 1, 152, 22))
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # check for collision with level objects
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 10
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.velocity_y = -10
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.velocity_y += gravity
        delta_x = self.direction * self.speed
        delta_y = self.velocity_y

        # check collision with level
        for tile in world.obstacle_list:
            # check collision with walls
            if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.width, self.height):
                self.direction *= -1
                delta_x = self.direction * self.speed
                # check for collision in the y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):
                    self.speed = 0
                    # check if below the ground (thrown up)
                    if self.velocity_y < 0:
                        self.velocity_y = 0
                        delta_y = tile[1].bottom - self.rect.top
                    # check if above the ground (falling)
                    elif self.velocity_y >= 0:
                        self.velocity_y = 0
                        delta_y = tile[1].top - self.rect.bottom
        # update grenade position
        self.rect.x += delta_x + screen_scroll
        self.rect.y += delta_y

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 1)
            explosion_group.add(explosion)
            # do damage to anyone who is nearby
            if abs(self.rect.centerx - player.rect.centerx) < tile_size * 2 and abs(
                    self.rect.centerx - player.rect.centerx) < tile_size * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < tile_size * 2 and abs(
                        self.rect.centerx - enemy.rect.centerx) < tile_size * 2:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(
                fr"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\img\explosion\exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        explosion_speed = 4
        # update explosion animation
        self.counter += 1
        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete, delete explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


# create screen fades
intro_fade = ScreenFade(1, black, 7)
death_fade = ScreenFade(2, red, 7)

# create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create empty tile list
world_data = []
for row in range(rows):
    r = [-1] * columns
    world_data.append(r)

# load in level data and create world
with open(fr"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\level{level}_data.csv",
          newline="") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

# run game functions
run = True
while run:
    clock.tick(FPS)

    if not start_game:
        # draw menu
        screen.fill(bg_color)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # update background
        # draw world map
        draw_background()
        world.draw()
        # show player health
        health_bar.draw(player.health)
        # show ammo
        draw_text("AMMO: ", font, white, 10, 30)
        for x in range(player.ammo):
            screen.blit(bullet_img, (85 + (x * 12), 48))
        # show grenades
        draw_text("GRENADES: ", font, white, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (120 + (x * 15), 70))

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # show intro
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # update player actions
        if player.alive:
            # shoot bullets
            if shoot:
                player.shoot()
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.7 * player.rect.size[0] * player.direction), player.rect.top,
                                  player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                player.grenades -= 1
            if player.in_air:
                player.update_action(2)  # 2 means "run"
            elif moving_left or moving_right:
                player.update_action(1)  # 1 means "run"
            else:
                player.update_action(0)  # 0 means "Idle"
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= max_levels:
                    # load in level data and create world
                    with open(fr"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\level{level}_data.csv",
                              newline="") as csv_file:
                        reader = csv.reader(csv_file, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # load in level data and create world
                    with open(fr"D:\PyCharm Community Edition 2020.3.1\PycharmProjects\Shooter\level{level}_data.csv",
                              newline="") as csv_file:
                        reader = csv.reader(csv_file, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        # to quit the game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
                shot_fx.play()
            if event.key == pygame.K_LCTRL:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_LCTRL:
                grenade = False
                grenade_thrown = False
    pygame.display.update()

pygame.quit()
