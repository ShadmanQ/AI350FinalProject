import math
import random
import pygame
from AIs import BasicAI
from AIs import Human
import tkinter as tk
from tkinter import messagebox


class cube(object):
    rows = 10
    w = 500

    def __init__(self, start, color=(255, 0, 0), dirnx=1, dirny=0):
        self.pos = start
        self.dirnx = 1
        self.dirny = 0
        self.color = color
        self.points = 1

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i * dis + centre - radius, j * dis + 8)
            circleMiddle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)


class fruit(cube):
    def __init__(self, start, params):
        cube.__init__(self, start, color=params[1])
        self.score = params[0]

    def hi(self):
        print("hi")


class snake(object):
    body = []
    turns = {}

    def __init__(self, color, pos, mind):
        self.color = color
        self.head = cube(pos, color)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
        self.mind = mind
        self.state_triple = [0, 0, 0]
        self.score = 0

    def move(self):
        print(self.state_triple)
        move = self.mind.get_move(self)

        if move == 'LEFT':
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif move == 'RIGHT':
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif move == 'UP':
            self.dirnx = 0
            self.dirny = -1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif move == 'DOWN':
            self.dirnx = 0
            self.dirny = 1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                if c.dirnx == -1 and c.pos[0] <= 0:
                    c.pos = (c.rows - 1, c.pos[1])
                elif c.dirnx == 1 and c.pos[0] >= c.rows - 1:
                    c.pos = (0, c.pos[1])
                elif c.dirny == 1 and c.pos[1] >= c.rows - 1:
                    c.pos = (c.pos[0], 0)
                elif c.dirny == -1 and c.pos[1] <= 0:
                    c.pos = (c.pos[0], c.rows - 1)
                else:
                    c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head = cube(pos, (255, 0, 0))
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1
        self.score = 0

    def growSnake(self, score):
        self.score += score
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            new = cube((tail.pos[0] - 1, tail.pos[1]), color=self.color)
            self.body.append(new)
        elif dx == -1 and dy == 0:
            new = cube((tail.pos[0] + 1, tail.pos[1]), color=self.color)
            self.body.append(new)
        elif dx == 0 and dy == 1:
            new = cube((tail.pos[0], tail.pos[1] - 1), color=self.color)
            self.body.append(new)
        elif dx == 0 and dy == -1:
            new = cube((tail.pos[0], tail.pos[1] + 1), self.color)
            self.body.append(new)

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

    def update_state(self, new_state):
        self.state_triple = new_state


def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, w))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (w, y))


def redrawWindow(surface, player, snack):
    global rows, width
    surface.fill((0, 0, 0))
    player.draw(surface)
    snack.draw(surface)
    drawGrid(width, rows, surface)
    pygame.display.update()


def randomSnack(rows, item):

    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
            continue
        else:
            break
    return (x, y)


def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass


def update_state(snake, snack):
    triple = [0, 0, 0]
    head = snake.body[0]
    if snake.dirnx == 1:
        if head.pos[0] == head.rows - 1:
            triple[1] = -1
        if head.pos[1] == 0:
            triple[0] = -1
        if head.pos[1] == head.rows - 1:
            triple[2] = -1
        if snack.pos == (head.pos[0] + 1, head.pos[1]):
            triple[1] = 1
        if snack.pos == (head.pos[0], head.pos[1] - 1):
            triple[0] = 1
        if snack.pos == (head.pos[0], head.pos[1] + 1):
            triple[2] = 1
    elif snake.dirnx == -1:
        if head.pos[0] == 0:
            triple[1] = -1
        if head.pos[1] == 0:
            triple[2] = -1
        if head.pos[1] == head.rows - 1:
            triple[0] = -1
        if snack.pos == (head.pos[0] - 1, head.pos[1]):
            triple[1] = 1
        if snack.pos == (head.pos[0], head.pos[1] - 1):
            triple[2] = 1
        if snack.pos == (head.pos[0], head.pos[1] + 1):
            triple[0] = 1
    elif snake.dirny == 1:
        if head.pos[1] == head.rows - 1:
            triple[1] = -1
        if head.pos[0] == 0:
            triple[2] = -1
        if head.pos[0] == head.rows - 1:
            triple[0] = - 1
        if snack.pos == (head.pos[0], head.pos[1] + 1):
            triple[1] = 1
        if snack.pos == (head.pos[0] - 1, head.pos[1]):
            triple[2] = 1
        if snack.pos == (head.pos[0] + 1, head.pos[1]):
            triple[0] = 1
    elif snake.dirny == -1:
        if head.pos[1] == 0:
            triple[1] = -1
        if head.pos[0] == 0:
            triple[0] = -1
        if head.pos[0] == head.rows - 1:
            triple[2] = - 1
        if snack.pos == (head.pos[0], head.pos[1] - 1):
            triple[1] = 1
        if snack.pos == (head.pos[0] - 1, head.pos[1]):
            triple[0] = 1
        if snack.pos == (head.pos[0] + 1, head.pos[1]):
            triple[2] = 1
    snake.update_state(triple)


def main():
    global width, rows
    fruits = [[1, (255, 0, 0)], [2, (0, 0, 255)], [3, (77, 77, 77)]]
    width = 500
    rows = 10
    win = pygame.display.set_mode((width, width))
    rand = BasicAI.BasicAI()
    human = Human.Human()
    player = snake((0, 0, 255), (5, 5), human)
    theFruit = fruit(randomSnack(rows, player), fruits[1])

    flag = True

    clock = pygame.time.Clock()

    while flag:
        pygame.time.delay(50)
        clock.tick(10)
        player.move()
        update_state(player, theFruit)
        # if head of snake and fruit overlap, grow
        if player.body[0].pos == theFruit.pos:
            player.growSnake(theFruit.score)
            theFruit = fruit(randomSnack(rows, player), fruits[2])

        for x in range(len(player.body)):
            if player.body[x].pos in list(map(lambda z: z.pos, player.body[x + 1:])):
                print('Score:', player.score)
                message_box('HA', 'You lost, loser')
                player.reset((10, 10))
                break

        redrawWindow(win, player, theFruit)

    pass


main()
