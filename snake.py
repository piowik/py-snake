# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 18:26:04 2016
@author: Piotrek
"""
import random
import threading

import pygame
import pygame.font

fullscreen = False
map_width = 1424
map_height = 768
offset_l = 208
offset_r = 208
item_dim = 16
step = item_dim
white = (255, 255, 255)
start_x = int((offset_l / item_dim))
end_x = int((map_width - offset_l - item_dim) / item_dim)
start_y = 0
end_y = int((map_height - item_dim) / item_dim)
center = [int(((end_x - 1) - (start_x + 1)) / 2) * item_dim, int(((end_y - 1) - (start_y + 1)) / 2) * item_dim]
menu_start_pos = 380  # main menu position
menu_vertical_offset = 30  # distance between menu items

game_name = "Py-Snake"
font_name = "PressStart2P.ttf"
logo_image = pygame.image.load('images/snakelogo.png')
body_image = pygame.image.load('images/body.png')
body_image_red = pygame.image.load('images/body_red.png')
head_image = pygame.image.load('images/head.png')
head_image_red = pygame.image.load('images/head_red.png')
background_image = pygame.image.load('images/gamebg.png')
walls_images = [pygame.image.load('images/walls.png'), pygame.image.load('images/wallc.png'),
                pygame.image.load('images/walle.png')]
bonuses_images = [pygame.image.load('images/apple.png'), pygame.image.load('images/bon_5.png'),
                  pygame.image.load('images/bon_speedup.png'),
                  pygame.image.load('images/bon_x2.png'), pygame.image.load('images/bon_speedup_r.png'),
                  pygame.image.load('images/bon_5_r.png'), pygame.image.load('images/bon_sleep_r.png'),
                  pygame.image.load('images/bomb.png')]

startlength = 1
apple_points = 10  # points for apples
apples_speed_increase = 2  # speed increase every apples_to_speedup set in diff settings

# 1 - apple, 2- +5len, 3 - speedup, 4 - scorex2, 5 - speedup R, 6 - +5len R, 7 - sleep R, 8 - bomb
singleplayer_bonuses = [2, 3, 4]  # available bonuses in singleplayer mode
multiplayer_bonuses = [2, 3, 4, 5, 6, 7]  # available bonuses in multiplayer mode
difficulty_settings = [[90, 40, 18, 3], [76, 90, 12, 2],
                       [100, 10, 25, 5]]  # start_to_move, bomb_chance, bonus_decay, apples_to_speedup

menu_items = []
snakes = []
walls = []
bonuses = []
random.seed()


def get_text_position(txt, pos, mode):
    text_size = [int(txt.get_rect().width), int(txt.get_rect().height)]
    if mode == "centerx":  # pos is ypos
        return [map_width / 2 - text_size[0] / 2, pos]
    elif mode == "centery":  # pos is xpos
        return [pos, map_height / 2 - text_size[1] / 2]
    elif mode == "centerxy":  # pos doesn't matter
        return [map_width / 2 - text_size[0] / 2, map_height / 2 - text_size[1] / 2]
    elif mode == "fitright":  # pos is ypos
        return [map_width - text_size[0], pos]
    raise ValueError('Mode value error.')


def draw_center_text(txt):
    text_renderer = font_big.render(txt, True, white)
    game_container.blit(text_renderer, get_text_position(text_renderer, 0, "centerxy"))


def progress_timer(val):
    s = "["
    for i in range(0, val):
        s += "|"
    for i in range(0, 10 - val):
        s += "."
    s += "]"
    return s


def use_bonuses():
    return False if menu_items[3].option == 1 else True


def use_walls():
    return False if menu_items[2].option == 1 else True


def update_difficulty(level):
    d_s_item = difficulty_settings[level]
    global start_to_move
    start_to_move = d_s_item[0]
    global bomb_chance
    bomb_chance = d_s_item[1]
    global bonus_decay
    bonus_decay = d_s_item[2]
    global apples_to_speedup
    apples_to_speedup = d_s_item[3]


def prep_walls():
    for x in range(start_x + 1, end_x):
        Wall([x * item_dim, start_y * item_dim], 0, 0)
        Wall([x * item_dim, end_y * item_dim], 0, 0)
    for y in range(start_y + 1, end_y):
        Wall([start_x * item_dim, y * item_dim], 0, 90)
        Wall([end_x * item_dim, y * item_dim], 0, 90)
    Wall([start_x * item_dim, start_y * item_dim], 1, 0)
    Wall([start_x * item_dim, end_y * item_dim], 1, 90)
    Wall([end_x * item_dim, start_y * item_dim], 1, 270)
    Wall([end_x * item_dim, end_y * item_dim], 1, 180)


def prepare_menu():
    MenuItem("Start game", "", menu_start_pos)
    MenuItem("Players ", ["one", "two"], menu_start_pos + (len(menu_items) * menu_vertical_offset))
    MenuItem("Walls ", ["yes", "no"], menu_start_pos + (len(menu_items) * menu_vertical_offset))
    MenuItem("Bonuses ", ["yes", "no"], menu_start_pos + (len(menu_items) * menu_vertical_offset))
    MenuItem("Difficulty ", ["normal", "hard", "easy"], menu_start_pos + (len(menu_items) * menu_vertical_offset))
    MenuItem("Quit", "", menu_start_pos + (len(menu_items) * menu_vertical_offset))


class MenuItem(object):
    def __init__(self, text, options, posy):
        menu_items.append(self)
        self.text = text
        self.options = options
        self.option = 0
        self.y = posy
        self.x = 0

    def draw(self):
        menu_text = self.text
        if len(self.options) > 0:
            menu_text += "( " + self.options[self.option] + " )"
        start_text = font_big.render(menu_text, True, white)
        text_position = get_text_position(start_text, self.y, "centerx")
        self.x = text_position[0]
        game_container.blit(start_text, (self.x, self.y))


def draw_menu(selection):
    text_color = white
    title = font_large.render(game_name, True, text_color)
    game_container.blit(title, get_text_position(title, menu_start_pos - 80, "centerx"))
    for menu_item in menu_items:
        menu_item.draw()
    menu_list = [font_big.render("P - Pause, Q - Return to menu", True, text_color),
                 font_big.render("Player 2, red: Arrow keys", True, text_color),
                 font_big.render("Player 1, green: W,A,S,D", True, text_color),
                 font_big.render("Game controls:", True, text_color),
                 font_big.render("W,S - Select menu item, E - Choose menu item", True, text_color)]
    for i, menu_item in enumerate(menu_list):
        game_container.blit(menu_item, get_text_position(menu_item, map_height - 30 - 25 * i, "centerx"))
    game_container.blit(font_big.render(")", True, text_color), [menu_items[selection].x - 20, menu_items[selection].y])


def build_score_list(snak, text_color, color):
    score_texts_list = [font.render(color + " snake", True, text_color),
                        font.render("Score: " + str(snak.score), True, text_color),
                        font.render("Length: " + str(snak.length), True, text_color),
                        font.render("Speed: " + str(start_to_move - snak.to_move), True, text_color)]
    if snak.powerup_speed:
        score_texts_list.append(font.render("Speed x2", True, text_color))
        score_texts_list.append(font.render(progress_timer(snak.powerup_speed), True, text_color))
    if snak.powerup_score:
        score_texts_list.append(font.render("Score x2", True, text_color))
        score_texts_list.append(font.render(progress_timer(snak.powerup_score), True, text_color))
    if snak.powerup_sleep:
        score_texts_list.append(font.render("Sleep", True, text_color))
        score_texts_list.append(font.render(progress_timer(snak.powerup_sleep), True, text_color))
    return score_texts_list


def show_score():
    s = pygame.Surface((180, 200), pygame.SRCALPHA)  # alpha
    s.fill((255, 255, 255, 64))  # incl alpha val
    game_container.blit(s, (22, 12))
    text = build_score_list(snakes[0], white, "Green")
    for i, item in enumerate(text):
        text_width = int(item.get_rect().width)
        game_container.blit(item, [offset_l - text_width - 10, 15 + (20 * i)])
    if len(snakes) > 1:
        s = pygame.Surface((180, 200), pygame.SRCALPHA)
        s.fill((255, 255, 255, 64))
        game_container.blit(s, (1221, 12))
        text = build_score_list(snakes[1], white, "Red")
        for i, item in enumerate(text):
            game_container.blit(item, [map_width - offset_r + 10, 15 + (20 * i)])


def show_game_over():
    text_color = white
    text = [font_large.render("GAME OVER", True, text_color)]
    if len(snakes) > 1:
        if not snakes[0].playing:
            text.append(font_big.render("Green snake crashed", True, text_color))
        if not snakes[1].playing:
            text.append(font_big.render("Red snake crashed", True, text_color))
    text.append(font_big.render("Green score: " + str(snakes[0].score), True, text_color))
    if len(snakes) > 1:
        text.append(font_big.render("Red score: " + str(snakes[1].score), True, text_color))
    text.append(font_big.render("Q - return to menu", True, text_color))
    for i, item in enumerate(text):
        game_container.blit(item, get_text_position(item, (map_height / 2 + (50 * i) - 100), "centerx"))
    show_score()


def powerup_tick(snake):
    if snake.powerup_score > 0:
        snake.powerup_score -= 1
        if snake.powerup_score == 0:
            snake.score_multiplier = 1.0
    if snake.powerup_speed > 0:
        snake.powerup_speed -= 1
        if snake.powerup_speed == 0:
            snake.speed_multiplier = 1.0
    if snake.powerup_sleep > 0:
        snake.powerup_sleep -= 2
    if snake.powerup_score > 0 or snake.powerup_speed > 0 or snake.powerup_sleep > 0:
        threading.Timer(0.5, powerup_tick, [snake]).start()
    else:
        snake.hasTimer = False


class Wall(object):
    def __init__(self, pos, d, rot):
        walls.append(self)
        self.x = pos[0]
        self.y = pos[1]
        self.type = d
        self.rot = rot
        self.rect = pygame.Rect(self.x, self.y, item_dim, item_dim)

    def draw(self):
        image = pygame.transform.rotate(walls_images[self.type], self.rot)
        game_container.blit(image, (self.x, self.y))


class Snake(object):
    def __init__(self, pos, head, body, move):
        snakes.append(self)
        self.snake_list = [pygame.Rect(pos[0], pos[1], item_dim, item_dim)]
        self.image_head = head
        self.image_body = body
        self.length = startlength
        self.score = 0
        self.playing = True
        self.direction = move
        self.next_direction = move
        self.since_last_move = 0  # time since last move
        self.to_move = start_to_move  # time between move
        self.apples_eaten = 0
        self.score_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.has_timer = False
        self.powerup_score = 0
        self.powerup_speed = 0
        self.powerup_sleep = 0

    def set_direction(self, direction):
        self.next_direction = direction

    def move(self):
        dx = 0
        dy = 0
        if self.powerup_sleep > 0:
            return
        if self.next_direction != self.direction:
            if self.length > 1:
                if not ((self.next_direction == 'a' and self.direction == 'd')
                        or (self.next_direction == 's' and self.direction == 'w')
                        or (self.next_direction == 'd' and self.direction == 'a')
                        or (self.next_direction == 'w' and self.direction == 's')):
                    self.direction = self.next_direction
            else:
                self.direction = self.next_direction
        if self.direction == 'd':
            dx = step
        elif self.direction == 'w':
            dy = -step
        elif self.direction == 's':
            dy = step
        elif self.direction == 'a':
            dx = -step
        head = self.snake_list[-1]
        new_item = pygame.Rect(head.x, head.y, item_dim, item_dim)
        new_item.x += dx
        new_item.y += dy
        if not use_walls():  # no walls
            if new_item.x > (map_width - offset_r - item_dim):
                new_item.x = offset_l
            if new_item.x < offset_l:
                new_item.x = map_width - offset_r - item_dim
            if new_item.y > (map_height - item_dim):
                new_item.y = 0
            if new_item.y < 0:
                new_item.y = map_height - item_dim
        self.snake_list.append(new_item)
        if len(self.snake_list) > self.length:
            self.snake_list.pop(0)
        self.check_collision()

    def check_collision(self):
        head = self.snake_list[-1]
        if use_walls():
            for wall in walls:
                if head.colliderect(wall.rect):
                    self.set_crashed()
        if len(snakes) > 1:
            if self == snakes[0]:
                target = snakes[1]
            else:
                target = snakes[0]
        for bonus in bonuses:
            if head.colliderect(bonus.rect):
                if bonus.type == 1:  # apple
                    place_object(1)
                    self.score += int(apple_points * self.score_multiplier)
                    self.length += 1
                    self.apples_eaten += 1
                    apples_eaten = self.apples_eaten
                    if len(snakes) > 1:
                        apples_eaten += target.apples_eaten
                    if apples_eaten % apples_to_speedup == 0:
                        for sn in snakes:
                            sn.add_speed(apples_speed_increase)
                    if use_bonuses():
                        objects = singleplayer_bonuses
                        if len(snakes) > 1:
                            objects = multiplayer_bonuses
                        bonuses_to_place = random.randint(0, 2)
                        for i in range(0, bonuses_to_place):
                            place_object(objects[random.randint(0, len(objects) - 1)])
                        if random.randint(0, 100) <= bomb_chance:
                            place_object(8)
                elif bonus.type == 2:
                    self.length += 5
                    self.score += int(60 * self.score_multiplier)
                elif bonus.type == 3:
                    self.add_powerup("speed")
                elif bonus.type == 4:
                    self.add_powerup("score")
                elif bonus.type == 5:
                    target.add_powerup("speed")
                elif bonus.type == 6:
                    target.length += 5
                elif bonus.type == 7:
                    target.add_powerup("sleep")
                elif bonus.type == 8:
                    self.set_crashed()
                bonuses.remove(bonus)

        for chunk in self.snake_list[:-1]:
            if head.colliderect(chunk):
                self.playing = False

        for eachsnake in snakes:
            if eachsnake == self:
                body = eachsnake.snake_list[:-1]
            else:
                body = eachsnake.snake_list
            for chunk in body:
                if head.colliderect(chunk):
                    self.set_crashed()

    def set_crashed(self):
        if len(snakes) > 1:
            if self == snakes[0]:
                target = snakes[1]
            else:
                target = snakes[0]
            target.score += 500
        self.playing = False

    def add_speed(self, dx):
        if self.to_move > 30:
            self.to_move -= dx

    def get_to_move(self):
        ret = int(self.to_move / self.speed_multiplier)
        if ret < 20:
            ret = 20
        return ret

    def add_powerup(self, powerup):
        if powerup == "score":
            self.score_multiplier = 2.0
            self.powerup_score = 10  # 5 seconds
        elif powerup == "speed":
            self.speed_multiplier = 2.0
            self.powerup_speed = 10
        elif powerup == "sleep":
            self.powerup_sleep = 10
        if not self.has_timer:
            self.has_timer = True
            powerup_tick(self)

    def draw(self):
        for snake_body in self.snake_list:
            if snake_body == self.snake_list[-1]:
                if self.direction == "s":
                    head = pygame.transform.rotate(self.image_head, 180)
                elif self.direction == "a":
                    head = pygame.transform.rotate(self.image_head, 90)
                elif self.direction == "d":
                    head = pygame.transform.rotate(self.image_head, 270)
                else:
                    head = self.image_head
                game_container.blit(head, (snake_body.x, snake_body.y))
            else:
                game_container.blit(self.image_body, (snake_body.x, snake_body.y))


class Bonus(object):
    def __init__(self, pos, d):
        bonuses.append(self)
        self.x = pos[0]
        self.y = pos[1]
        self.type = d
        self.time = bonus_decay * 1000
        if d == 8:  # bomb
            self.time = self.time * 2
        self.rect = pygame.Rect(self.x, self.y, item_dim, item_dim)

    def draw(self):
        game_container.blit(bonuses_images[self.type - 1], (self.x, self.y))


def place_object(object_type):
    posx = random.randint(start_x + 1, end_x - 1) * item_dim
    posy = random.randint(start_y + 1, end_y - 1) * item_dim
    check_pos = pygame.Rect(posx, posy, item_dim, item_dim)
    collided = False
    for each_snake in snakes:
        for chunk in each_snake.snake_list:
            if check_pos.colliderect(chunk):
                collided = True
                break
    if not collided:
        Bonus([posx, posy], object_type)
    else:
        place_object(object_type)


def game_menu():
    menu = True
    selection = 0
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if selection > 0:
                        selection -= 1
                if event.key == pygame.K_e:
                    if selection == 0:  # pos 0 - start
                        update_difficulty(menu_items[4].option)
                        play_loop(menu_items[1].option + 1)
                    elif menu_items[selection].text == "Quit":
                        menu = False
                    else:
                        menu_items[selection].option = (menu_items[selection].option + 1) % (
                            len(menu_items[selection].options))
                if event.key == pygame.K_s:
                    if selection < len(menu_items) - 1:
                        selection += 1
            if event.type == pygame.QUIT:
                menu = False
        game_container.blit(background_image, (0, 0))
        game_container.blit(logo_image, (350, 40))
        draw_menu(selection)
        pygame.display.update()


def pause_menu():
    pause = True
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = False
        draw_center_text("Pause")
        pygame.display.update()


def draw_game_area():
    game_container.blit(background_image, (0, 0))
    if use_walls():
        for wall in walls:
            wall.draw()


def init_snakes(snakes_no):
    snakes.clear()
    Snake([offset_l + center[0] - 2 * item_dim, center[1] - 2 * item_dim], head_image, body_image, 'w')
    if snakes_no > 1:
        Snake([offset_l + center[0] + 2 * item_dim, center[1] + 2 * item_dim], head_image_red, body_image_red, 's')


def play_loop(snakes_no):
    play = True
    init_snakes(snakes_no)
    bonuses.clear()
    place_object(1)
    countdown = 3
    while play:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if play:
                        pause_menu()
                if event.key == pygame.K_w:
                    snakes[0].set_direction('w')
                if event.key == pygame.K_a:
                    snakes[0].set_direction('a')
                if event.key == pygame.K_s:
                    snakes[0].set_direction('s')
                if event.key == pygame.K_d:
                    snakes[0].set_direction('d')
                if len(snakes) > 1:
                    if event.key == pygame.K_UP:
                        snakes[1].set_direction("w")
                    if event.key == pygame.K_LEFT:
                        snakes[1].set_direction("a")
                    if event.key == pygame.K_DOWN:
                        snakes[1].set_direction("s")
                    if event.key == pygame.K_RIGHT:
                        snakes[1].set_direction("d")
                if event.key == pygame.K_q:
                    play = False
        draw_game_area()
        if len(snakes) > 0:
            game_over = False
            for eachsnake in snakes:
                if eachsnake.playing is False:
                    game_over = True
                    break
            if not game_over:
                for s in snakes:
                    if s.since_last_move > s.get_to_move():
                        s.since_last_move = 0
                        s.move()
                for bonus in bonuses:
                    bonus.draw()
                for eachsnake in snakes:
                    eachsnake.draw()
                show_score()
            else:
                show_game_over()
        pygame.display.update()
        while countdown > 0:
            draw_game_area()
            draw_center_text(str(countdown))
            for eachsnake in snakes:
                eachsnake.draw()
            show_score()
            countdown -= 1
            pygame.display.update()
            clock.tick(1)
        dt = clock.tick(100)
        for sn in snakes:
            sn.since_last_move += dt
        for bonus in bonuses:
            if bonus.type != 1:
                bonus.time -= dt
                if bonus.time < 0:
                    bonuses.remove(bonus)


pygame.init()
font = pygame.font.Font(font_name, 13)
font_big = pygame.font.Font(font_name, 20)
font_large = pygame.font.Font(font_name, 48)
if fullscreen:
    game_container = pygame.display.set_mode((map_width, map_height), pygame.FULLSCREEN)
else:
    game_container = pygame.display.set_mode((map_width, map_height))
pygame.display.set_caption(game_name)
clock = pygame.time.Clock()
prep_walls()
prepare_menu()
game_menu()
pygame.quit()
quit()
