import pygame
import sys
import time
import random
from pygame.locals import *
import threading
import numpy as np

#COLORS :: RGB VALUES

# fruit color
fruitColor = (255, 147, 59) #pink

# primary snake color
snakeColor1 = (70, 74, 224)
#secondary snake color
snakeColor2 = (143, 145, 247)
# snake head color
snakeHeadColor = (220,220,220) #light gray

# background color
backgroundColor = (0,0,0) #black


#enviromenment class
class game_ai:
    def __init__(self, display_width=640, display_height=480):

        # Initailize pygame
        
        # clock and framerate
        self.FPS = 40
        self.fpsClock = pygame.time.Clock()

        self.display_width = display_width
        self.display_height = display_height
        self.board = pygame.display.set_mode((self.display_width, self.display_height))

        self.__init_game()

    def __init_game(self):
        self.y_change = 0
        self.x_change = 20

        # Initialize initial position and object size
        self.snakePosition = [random.randint(4,5)*20, random.randint(4,5)*20] # Snake head
        self.snakeSegments = [[self.snakePosition[0], self.snakePosition[1]], 
                        [self.snakePosition[0]-20, self.snakePosition[1]], 
                        [self.snakePosition[0]-40, self.snakePosition[1]]]

        self.fruitPosition = [random.randint(0, (self.display_width-20)//20)*20, random.randint(0, (self.display_height-20)//20)*20]
        #
        self.fruitSpawned = 1

        #initially snake is moving straight
        self.action = [1, 0, 0] # [straight, right, left]
        self.score = 0
        self.episode = 0

    def frameStep(self, action):
        self.action = action
        reward, done, score = self.play(self.board, self.action)
        return reward, done, score

    def reset(self):
        score1 = self.score
        self.__init_game()
        return score1

    # Snake and fruit
    def play(self, board, action):
        self.episode += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))
        
        self.move(action)
        reward = 0
        self.snakeSegments.insert(0, list(self.snakePosition))
        if self.snakePosition[0] == self.fruitPosition[0] and self.snakePosition[1] == self.fruitPosition[1]:
            self.fruitSpawned = 0
            reward = 10
        else:
            self.snakeSegments.pop()


        if self.fruitSpawned == 0:
            x = random.randrange(0, (self.display_width-20)//20)
            y = random.randrange(0, (self.display_height-20)//20)
            self.fruitPosition = [int(x*20), int(y*20)]
            self.fruitSpawned = 1
            self.score += 1

        #REFRESH FRAME

        #draw board
        board.fill(backgroundColor)

        #draw snake body
        for position in self.snakeSegments[1:]:
            pygame.draw.rect(self.board, snakeColor2, Rect(position[0], position[1], 20, 20))
            pygame.draw.rect(self.board, snakeColor1, Rect(position[0]+4, position[1]+4, 12, 12))

        pygame.draw.rect(self.board, snakeHeadColor, Rect(self.snakePosition[0], self.snakePosition[1], 20, 20))
        pygame.draw.rect(self.board, fruitColor, Rect(self.fruitPosition[0], self.fruitPosition[1], 20, 20))
        pygame.display.flip()

        done = False

        
        if self.episode > 100*len(self.snakeSegments):
            done = True
            reward = -10
            return reward, done, self.score
        
        if self.snakePosition[0]>self.display_width-20 or self.snakePosition[0]<0:
            done = True
            reward = -10
            return reward, done, self.score 

        if self.snakePosition[1]>self.display_height-20 or self.snakePosition[1]<0:
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
        #[straight, right, left]
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


