import torch
import torch.nn as nn
import torch.nn.functional as F

import torch.optim as optim
from torch.utils.data import DataLoader

import random
import os
import pygame
import sys

import numpy as np
import matplotlib.pyplot as plt

from operator import add
from collections import deque

from snake_ai2 import game_ai

random.seed(9001)

# NETWORK


class QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x = self.linear1(x)
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x


class DQNAgent_train(object):

    def __init__(self):
        self.gamma = 0.9
        self.epsilon = 0
        self.counter_games = 0
        self.memory = deque()
        self.lr = 1e-4
        self.model = QNet(11, 256, 3)
        self.model.train()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.loss_fn = nn.MSELoss()


    def remember(self, state, action, reward, next_state, done):
        self.memory.append([state, action, reward, next_state, done])
        if len(self.memory) > 100000:
            self.memory.popleft()

    def train_long_memory(self, memory):
        self.counter_games += 1
        if len(memory) > 1000:
            minibatch = random.sample(memory, 1000)
        else:
            minibatch = memory

        state, action, reward, next_state, done = zip(*minibatch)
        state = torch.tensor(state, dtype=torch.float)  # [1, ... , 0]
        action = torch.tensor(action, dtype=torch.long)  # [1, 0, 0]
        reward = torch.tensor(reward, dtype=torch.float)  # int
        next_state = torch.tensor(next_state, dtype=torch.float)  # [True, ... , False]
        target = reward
        target = reward + self.gamma * torch.max(self.model(next_state), dim=1)[0]
        location = [[x] for x in torch.argmax(action, dim=1).numpy()]
        location = torch.tensor(location)
        pred = self.model(state).gather(1, location)  # [action]
        pred = pred.squeeze(1)
        loss = self.loss_fn(target, pred)
        loss.backward()
        self.optimizer.step()

    def train_short_memory(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        target = reward

        if not done:
            target = reward + self.gamma * torch.max(self.model(next_state))
        pred = self.model(state)
        target_f = pred.clone()
        target_f[torch.argmax(action).item()] = target
        loss = self.loss_fn(target_f, pred)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def plot(self, score, mean_per_game):
        from IPython import display
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of Games')
        plt.ylabel('Score')
        plt.plot(score)
        plt.plot(mean_per_game)
        plt.ylim(ymin=0)
        plt.text(len(score) - 1, score[-1], str(score[-1]))
        plt.text(len(mean_per_game) - 1, mean_per_game[-1], str(mean_per_game[-1]))

    def get_action(self, state):
        self.epsilon = 80 - self.counter_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] += 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] += 1
        return final_move


def train(num_fruit, num_snakes):
    pygame.display.set_caption('Training!')
    # Load image and set icon
    image = pygame.image.load('snake.png')
    pygame.display.set_icon(image)
    model_folder_path = './model'
    if not os.path.exists(model_folder_path):
        os.makedirs(model_folder_path)
    plt.ion()
    pygame.init()
    score_plot = []
    total_score = 0
    mean_plot = []
    record = 0
    agent = DQNAgent_train()
    game = game_ai(num_fruit, num_snakes)
    while True:
        old_states = []
        final_moves = []
        for snake in game.snakes:
            # get old state
            state_old = game.get_state(snake)
            old_states.append(state_old)

            final_moves.append(agent.get_action(state_old))

            # perform new move and get new state
        rewards, dones, scores = game.frameStep(final_moves)
        for i in range(len(game.snakes)):
            state_new = game.get_state(game.snakes[i])

            # train short memory base on the new action and state
            agent.train_short_memory(old_states[i], final_moves[i], rewards[i], state_new, dones[i])

            # store the new data into a long term memory
            agent.remember(old_states[i], final_moves[i], rewards[i], state_new, dones[i])

        if not game.snakes:
            # One game is over, train on the memory and plot the result.
            scores = game.reset()
            sc = max(scores)
            total_score += sc
            agent.train_long_memory(agent.memory)
            print('Game', agent.counter_games, '      Score:', sc)
            if sc > record:
                record = sc
                name = 'best_model.pth'.format(sc)
                dir = os.path.join(model_folder_path, name)
                torch.save(agent.model.state_dict(), dir)
            print('record: ', record)
            score_plot.append(sc)
            mean = total_score / agent.counter_games
            mean_plot.append(mean)
            agent.plot(score_plot, mean_plot)

    plt.ioff()
    plt.show()


if __name__ == '__main__':
    pygame.display.set_caption('Deep Q Snake!')
    image = pygame.image.load('snake.png')
    args = sys.argv
    num_fruit = int(args[1])
    num_snakes = int(args[2])
    pygame.display.set_icon(image)
    pygame.init()
    train(num_fruit, num_snakes)
