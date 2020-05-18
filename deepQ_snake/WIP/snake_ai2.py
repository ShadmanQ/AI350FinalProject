import pygame
import sys
import time
import random
from pygame.locals import *
import threading
import numpy as np
import math

# COLORS
# RED
redColour = pygame.Color(200, 0, 0)
brightRedColour = pygame.Color(255, 0, 0)
# GREEN
brightGreenColour = pygame.Color(0, 255, 0)
greenColour = pygame.Color(0, 200, 0)
brightGreenColour1 = (150, 255, 150)
darkGreenColour1 = (0, 155, 0)
# BLACK
blackColour = pygame.Color(0, 0, 0)
# WHITE
whiteColour = pygame.Color(255, 255, 255)
# GRAY
greyColour = pygame.Color(150, 150, 150)
LightGrey = pygame.Color(220, 220, 220)
# YELLOW
yellowColour = pygame.Color(255, 255, 0)
blueColour = pygame.Color(0, 0, 255)
purpleColour = pygame.Color(255, 0, 255)


class game_ai:

    def __init__(self, num, display_width=640, display_height=480):
        # Initailize pygame

        self.FPS = 40
        self.fpsClock = pygame.time.Clock()

        self.numFruit = num
        self.closestFruit = []
       # rewards = [10, 20, 30]
        self.colours = [redColour, blueColour, yellowColour]

        self.display_width = display_width
        self.display_height = display_height
        self.playSurface = pygame.display.set_mode((self.display_width, self.display_height))
        self.__init_game()

    def __init_game(self):
        self.y_change = 0
        self.x_change = 20

        # Initialize initial position and object size
        self.snakePosition = [random.randint(4, 5) * 20, random.randint(4, 5) * 20]  # Snake head
        self.snakeSegments = [[self.snakePosition[0], self.snakePosition[1]],
                              [self.snakePosition[0] - 20, self.snakePosition[1]],
                              [self.snakePosition[0] - 40, self.snakePosition[1]]]

        self.fruitPositions = []  # holds the fruit positions
        self.fruitRewards = {}  # holds the reward for each fruit. key is reward, val is x y coord
        # there's probably a better way to organize this but my brain is frazzled

        # give each fruit it's own position on
        for i in range(self.numFruit):
            coord = [random.randint(
                0, (self.display_width - 20) // 20) * 20, random.randint(0, (self.display_height - 20) // 20) * 20]
            self.fruitPositions.append(coord)
            self.fruitRewards[(i + 1) * 10] = coord

        self.getClosestFruit()

    #    self.raspberryPosition = [random.randint(
    #        0, (self.display_width - 20) // 20) * 20, random.randint(0, (self.display_height - 20) // 20) * 20]
        self.raspberrySpawned = 1
        self.action = [1, 0, 0]  # [straight, right, left]
        self.score = 0
        self.episode = 0

    def frameStep(self, action):
        self.action = action
        reward, done, score = self.play(self.playSurface, self.action)
        return reward, done, score

    def reset(self):
        score1 = self.score
        self.__init_game()
        return score1

    # gets the Euclidean distance of each fruit relative to snakePosition
    def getClosestFruit(self):
        closest = 100000000000000  # set to arbitrarily large
        position = []
        for i in range(len(self.fruitPositions)):
            dist = math.sqrt(abs(self.snakePosition[0] - self.fruitPositions[i][0])
                             ** 2 + abs(self.snakePosition[1] - self.fruitPositions[i][1])**2)
            if dist < closest:
                closest = dist
                position = self.fruitPositions[i]
        self.closestFruit = position

    # Snake and raspberry
    def play(self, playSurface, action):
        self.episode += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

        self.getClosestFruit()
        self.move(action)
        reward = 0
        self.snakeSegments.insert(0, list(self.snakePosition))
        for fruit in self.fruitPositions:
            if fruit[0] == self.snakePosition[0] and self.snakePosition[1] == fruit[1]:
                self.raspberrySpawned = 0
                for key in self.fruitRewards.keys():
                    if self.fruitRewards[key] == fruit:
                        reward = key
               # reward = 10
        # if self.snakePosition[0] == self.raspberryPosition[0] and self.snakePosition[1] == self.raspberryPosition[1]:
        #     self.raspberrySpawned=0
        #     reward=10
        else:
            self.snakeSegments.pop()

        if self.raspberrySpawned == 0:
            for i in range(len(self.fruitPositions)):
                x = random.randrange(0, (self.display_width - 20) // 20)
                y = random.randrange(0, (self.display_height - 20) // 20)
                self.fruitPositions[i] = [int(x * 20), int(y * 20)]
                self.fruitRewards[i + 1 * 10] = [x, y]
            self.raspberrySpawned = 1
            self.score += 1

        #
        # if self.raspberrySpawned == 0:
        #     x=random.randrange(0, (self.display_width - 20) // 20)
        #     y=random.randrange(0, (self.display_height - 20) // 20)
        #     self.raspberryPosition=[int(x * 20), int(y * 20)]
        #     self.raspberrySpawned=1
        #     self.score += 1

        # refresh frame
        playSurface.fill(blackColour)
        for position in self.snakeSegments[1:]:
            pygame.draw.rect(self.playSurface, darkGreenColour1,
                             Rect(position[0], position[1], 20, 20))
            pygame.draw.rect(self.playSurface, brightGreenColour1,
                             Rect(position[0] + 4, position[1] + 4, 12, 12))

        pygame.draw.rect(self.playSurface, LightGrey, Rect(
            self.snakePosition[0], self.snakePosition[1], 20, 20))
        for i in range(len(self.fruitPositions)):
            pygame.draw.rect(self.playSurface, self.colours[i], Rect(
                self.fruitPositions[i][0], self.fruitPositions[i][1], 20, 20))
#        pygame.draw.rect(self.playSurface, redColour, Rect(
#            self.raspberryPosition[0], self.raspberryPosition[1], 20, 20))
        pygame.display.flip()

        done = False

        if self.episode > 100 * len(self.snakeSegments):
            done = True
            reward = -10
            return reward, done, self.score

        if self.snakePosition[0] > self.display_width - 20 or self.snakePosition[0] < 0:
            done = True
            reward = -10
            return reward, done, self.score

        if self.snakePosition[1] > self.display_height - 20 or self.snakePosition[1] < 0:
            done = True
            reward = -10
            return reward, done, self.score

        for snakeBody in self.snakeSegments[1:]:
            if self.snakePosition[0] == snakeBody[0] and self.snakePosition[1] == snakeBody[1]:
                done = True
                reward = -10
                return reward, done, self.score

        self.fpsClock.tick(self.FPS)

        return reward, done, self.score

    def move(self, action):
        # [straight, right, left]
        move_array = [self.x_change, self.y_change]
        # no change
        if np.array_equal(action, [1, 0, 0]):
            move_array = self.x_change, self.y_change

        # horizontal right
        elif np.array_equal(action, [0, 1, 0]) and self.y_change == 0:
            move_array = [0, self.x_change]
        # vertical right
        elif np.array_equal(action, [0, 1, 0]) and self.x_change == 0:
            move_array = [-self.y_change, 0]
        # horizontal left
        elif np.array_equal(action, [0, 0, 1]) and self.y_change == 0:
            move_array = [0, -self.x_change]
        # vertical left
        elif np.array_equal(action, [0, 0, 1]) and self.x_change == 0:
            move_array = [self.y_change, 0]

        self.x_change, self.y_change = move_array
        self.snakePosition[0] += self.x_change
        self.snakePosition[1] += self.y_change
