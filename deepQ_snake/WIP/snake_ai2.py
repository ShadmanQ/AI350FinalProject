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

    def __init__(self, num_fruit, num_snakes, display_width=640, display_height=480):
        # Initailize pygame
        self.FPS = 40
        self.fpsClock = pygame.time.Clock()

        self.numFruit = num_fruit
        self.numSnakes = num_snakes

        self.display_width = display_width
        self.display_height = display_height
        self.playSurface = pygame.display.set_mode((self.display_width, self.display_height))
        self.__init_game()

    def __init_game(self):
        self.final_scores = []
        self.fruitPositions = []
        self.snakes = []

        for i in range(self.numSnakes):
            intersect = True
            while intersect:
                intersect = False
                new_snake = Snake()
                for snake in self.snakes:
                    new_intersect = new_snake.intersects_other(snake) and snake.intersects_other(new_snake)
                    intersect = intersect or new_intersect
            self.snakes.append(new_snake)


        for i in range(self.numFruit):
            self.fruitPositions.append([random.randint(
                0, (self.display_width - 20) // 20) * 20, random.randint(0, (self.display_height - 20) // 20) * 20])

        for snake in self.snakes:
            snake.getClosestFruit(self.fruitPositions)

    #    self.raspberryPosition = [random.randint(
    #        0, (self.display_width - 20) // 20) * 20, random.randint(0, (self.display_height - 20) // 20) * 20]
        self.raspberrySpawned = 1
        self.action = [1, 0, 0]  # [straight, right, left]
        self.episode = 0

    def frameStep(self, actions):
        self.actions = actions
        reward, done, score = self.play(self.playSurface, self.actions)
        return reward, done, score

    def reset(self):
        scores = self.final_scores
        self.__init_game()
        return scores


    # Snake and raspberry
    def play(self, playSurface, actions):
        self.episode += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

        for snake in self.snakes:
            snake.getClosestFruit(self.fruitPositions)
        for i in range(len(self.snakes)):
            self.snakes[i].move(actions[i])
        for snake in self.snakes:
            snake.snakeSegments.insert(0, list(snake.snakePosition))
            eaten_fruits = []
            for fruit in self.fruitPositions:
                if fruit[0] == snake.snakePosition[0] and snake.snakePosition[1] == fruit[1]:
                    self.raspberrySpawned = 0
                    snake.eaten = True
                    snake.score += 1
                    eaten_fruits.append(fruit)
            # if self.snakePosition[0] == self.raspberryPosition[0] and self.snakePosition[1] == self.raspberryPosition[1]:
            #     self.raspberrySpawned=0
            #     reward=10
            if snake.eaten:
                for fruit in eaten_fruits:
                    self.fruitPositions.remove(fruit)
            else:
                snake.snakeSegments.pop()

        if self.raspberrySpawned == 0:
            while len(self.fruitPositions) < self.numFruit:
                x = random.randrange(0, (self.display_width - 20) // 20)
                y = random.randrange(0, (self.display_height - 20) // 20)
                self.fruitPositions.append([int(x * 20), int(y * 20)])
            self.raspberrySpawned = 1

        #
        # if self.raspberrySpawned == 0:
        #     x=random.randrange(0, (self.display_width - 20) // 20)
        #     y=random.randrange(0, (self.display_height - 20) // 20)
        #     self.raspberryPosition=[int(x * 20), int(y * 20)]
        #     self.raspberrySpawned=1
        #     self.score += 1

        # refresh frame
        playSurface.fill(blackColour)
        for snake in self.snakes:
            for position in snake.snakeSegments[1:]:
                pygame.draw.rect(self.playSurface, darkGreenColour1,
                                Rect(position[0], position[1], 20, 20))
                pygame.draw.rect(self.playSurface, brightGreenColour1,
                                Rect(position[0] + 4, position[1] + 4, 12, 12))

            pygame.draw.rect(self.playSurface, LightGrey, Rect(
                            snake.snakePosition[0], snake.snakePosition[1], 20, 20))
        for fruit in self.fruitPositions:
            pygame.draw.rect(self.playSurface, purpleColour, Rect(
                fruit[0], fruit[1], 20, 20))
#        pygame.draw.rect(self.playSurface, redColour, Rect(
#            self.raspberryPosition[0], self.raspberryPosition[1], 20, 20))
        pygame.display.flip()

        rewards = []
        dones = []
        scores = []
        dead = []

        for snake in self.snakes:
            enemies = self.snakes.copy()
            enemies.remove(snake)
            done = False
            reward = 0

            if self.episode > 100 * len(snake.snakeSegments):
                done = True
                reward = -10
                dead.append(snake)

            elif snake.snakePosition[0] > self.display_width - 20 or snake.snakePosition[0] < 0:
                done = True
                reward = -10
                dead.append(snake)

            elif snake.snakePosition[1] > self.display_height - 20 or snake.snakePosition[1] < 0:
                done = True
                reward = -10
                dead.append(snake)

            elif snake.eaten:
                reward = 10
                snake.eaten = False

            else:
                for enemy in enemies:
                    if snake.intersects_other(enemy):
                        done = True
                        reward = -10
                        dead.append(snake)
                if snake.intersects_self():
                    done = True
                    reward = -10
                    dead.append(snake)
            rewards.append(reward)
            dones.append(done)
            scores.append(snake.score)
        for snake in set(dead):
            self.final_scores.append(snake.score)
            self.snakes.remove(snake)

        self.fpsClock.tick(self.FPS)

        return rewards, dones, scores

    def get_state(self, snake):
        state = [
            # Snake location
            self.toForward(snake),

            self.toLeft(snake),

            self.toRight(snake),

            # Move direction
            snake.x_change == -20,
            snake.x_change == 20,
            snake.y_change == -20,
            snake.y_change == 20,
            # Raspberry location
            # snake.raspberryPosition[0] < snake.snakePosition[0],  # food left
            # snake.raspberryPosition[0] > snake.snakePosition[0],  # food right
            # snake.raspberryPosition[1] < snake.snakePosition[1],  # food up
            # snake.raspberryPosition[1] > snake.snakePosition[1],  # food down


            snake.closestFruit[0] < snake.snakePosition[0],
            snake.closestFruit[0] > snake.snakePosition[0],
            snake.closestFruit[1] < snake.snakePosition[1],
            snake.closestFruit[1] > snake.snakePosition[1]

        ]

        for i in range(len(state)):
            if state[i]:
                state[i] = 1
            else:
                state[i] = 0

        return np.asarray(state)

    def toForward(self,snake):
        oob = False
        if snake.x_change == 20 and snake.y_change == 0:
            forward_tile = [snake.snakeSegments[0][0] + 20, snake.snakeSegments[0][1]]
            oob = forward_tile[0] >= (self.display_width - 20)
        elif snake.x_change == -20 and snake.y_change == 0:
            forward_tile = [snake.snakeSegments[0][0] - 20, snake.snakeSegments[0][1]]
            oob = forward_tile[0] < 20
        elif snake.x_change == 0 and snake.y_change == -20:
            forward_tile = [snake.snakeSegments[0][0],snake.snakeSegments[0][1] - 20]
            oob = forward_tile[1] < 20
        elif snake.x_change == 0 and snake.y_change == 20:
            forward_tile = [snake.snakeSegments[0][0], snake.snakeSegments[0][1] + 20]
            oob = forward_tile[1] > self.display_height - 20
        else:
            print('Something has gone terribly wrong')
        if oob:
            return oob
        else:
            for other_snake in self.snakes:
                for seg in snake.snakeSegments:
                    if seg == forward_tile:
                        return True
        return False


    def toLeft(self,snake):
        oob = False
        if snake.x_change == 20 and snake.y_change == 0:
            left_tile = [snake.snakeSegments[0][0], snake.snakeSegments[0][1] - 20]
            oob = left_tile[1] < 20
        elif snake.x_change == -20 and snake.y_change == 0:
            left_tile = [snake.snakeSegments[0][0], snake.snakeSegments[0][1] + 20]
            oob = left_tile[1] > self.display_height - 20
        elif snake.x_change == 0 and snake.y_change == -20:
            left_tile = [snake.snakeSegments[0][0] - 20,snake.snakeSegments[0][1]]
            oob = left_tile[0] < 20
        elif snake.x_change == 0 and snake.y_change == 20:
            left_tile = [snake.snakeSegments[0][0] + 20, snake.snakeSegments[0][1]]
            oob = left_tile[0] > self.display_width - 20
        else:
            print('Something has gone terribly wrong')
        if oob:
            return oob
        else:
            for other_snake in self.snakes:
                for seg in snake.snakeSegments:
                    if seg == left_tile:
                        return True
        return False


    def toRight(self,snake):
        oob = False
        if snake.x_change == 20 and snake.y_change == 0:
            right_tile = [snake.snakeSegments[0][0], snake.snakeSegments[0][1] + 20]
            oob = right_tile[1] > self.display_height - 20
        elif snake.x_change == -20 and snake.y_change == 0:
            right_tile = [snake.snakeSegments[0][0], snake.snakeSegments[0][1] - 20]
            oob = right_tile[1] < 0
        elif snake.x_change == 0 and snake.y_change == -20:
            right_tile = [snake.snakeSegments[0][0] + 20,snake.snakeSegments[0][1]]
            oob = right_tile[0] > self.display_width - 20
        elif snake.x_change == 0 and snake.y_change == 20:
            right_tile = [snake.snakeSegments[0][0] - 20, snake.snakeSegments[0][1]]
            oob = right_tile[0] < 20
        else:
            print('Something has gone terribly wrong')
        if oob:
            return oob
        else:
            for other_snake in self.snakes:
                for seg in snake.snakeSegments:
                    if seg == right_tile:
                        return True
        return False




class Snake:

    def __init__(self):
        self.score = 0
        self.closestFruit = []
        self.y_change = 0
        self.x_change = 20
        self.eaten = False
        self.dead = False

        # Initialize initial position and object size
        self.snakePosition = [random.randint(1, 9) * 20, random.randint(1, 9) * 20]  # Snake head
        self.snakeSegments = [[self.snakePosition[0], self.snakePosition[1]],
                              [self.snakePosition[0] - 20, self.snakePosition[1]],
                              [self.snakePosition[0] - 40, self.snakePosition[1]]]

    def getClosestFruit(self,fruits):
        closest = 100000000000000  # set to arbitrarily large
        position = []
        for fruit in fruits:
            dist = math.sqrt(abs(self.snakePosition[0] - fruit[0])
                             ** 2 + abs(self.snakePosition[1] - fruit[1])**2)
            if dist < closest:
                closest = dist
                position = fruit
        self.closestFruit = position

    def intersects_other(self,snake):
        for segment in snake.snakeSegments:
            if self.snakePosition == segment:
                return True
        return False

    def intersects_self(self):
        for segment in self.snakeSegments[1:]:
            if self.snakePosition == segment:
                return True
        return False

    def move(self, action):
        # [straight, right, left]
        if not self.dead:
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
