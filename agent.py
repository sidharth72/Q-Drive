import torch
import random
import numpy as np
from collections import deque
from model import QNet, QTrainer
from game import CarGame


MAX_MEMORY = 100000
BATCH_SIZE = 512
LR = 0.001


# Load the pretrained model, else initialize new model
model = QNet(13, 3)
try:
    model.load_state_dict(torch.load('model/model.pth'))
except:
    pass

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.01
        self.gamma = 0.9
        self.memory = deque(maxlen = MAX_MEMORY)
        self.model = model
        self.trainer = QTrainer(self.model, lr = LR, gamma = self.gamma)


    def get_state(self, game):
        return game.get_game_state()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long(self):
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)
        else:
            sample = self.memory

        states, actions, rewards, next_states, dones = zip(*sample)

        self.trainer.train_step(states, actions, rewards, next_states, dones)
        
    def train_short(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        if random.random() < self.epsilon:
            # Exploration : Take random moves for exploring the environment
            move = random.randint(0, 2)

        else:

            # Exploitation : Use the learned policy from the network to take action
            state = torch.tensor(state, dtype=torch.float).unsqueeze(0)
            prediction = self.model(state)
            move = torch.argmax(prediction).item()
        return move


def train():
    record = 0
    agent = Agent()
    game = CarGame()

    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        state_new, reward, score, done = game.game_step(final_move)

        # Train the short term memory with current environmental conditions
        agent.train_short(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1

            # Train Batches
            agent.train_long()

            if agent.epsilon > agent.min_epsilon:
                agent.epsilon *= agent.epsilon_decay
                
            if score > record:
                record = score
                agent.model.save()

            print("game", agent.n_games, 'score', score, 'record', record)

if __name__ == "__main__":
    train()