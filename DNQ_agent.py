from collections import deque

import numpy as np
import torch
import torch.nn as nn
import random

from torch import optim

ACTIONS = [
    None,
    "LEFT",
    "RIGHT",
    "ROTATE_R",
    "ROTATE_L",
    "ROTATE_180",
    "SOFT_DROP",
    "HARD_DROP",
    "HOLD"
]


class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()

        self.network=nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),

            nn.Linear(256, 256),
            nn.ReLU(),

            nn.Linear(256, output_size)
        )

    def forward(self, state):
        return self.network(state)

class ReplayBuffer:
    def __init__(self, capacity, state_size, device):
        self.device = device
        self.capacity = capacity
        self.states = torch.zeros((capacity, state_size), device=device)
        self.next_states = torch.zeros((capacity, state_size), device=device)
        self.actions = torch.zeros(capacity, dtype=torch.int64, device=device)
        self.rewards = torch.zeros(capacity, device=device)
        self.dones = torch.zeros(capacity, device=device)
        self.position = 0
        self.size = 0

    def add(self, s, a, r, ns, d):
        i = self.position
        self.states[i] = torch.as_tensor(s, device=self.device)
        self.next_states[i] = torch.as_tensor(ns, device=self.device)
        self.actions[i] = a
        self.rewards[i] = r
        self.dones[i] = float(d)
        self.position = (i + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size):
        idx = torch.randint(0, self.size, (batch_size,), device=self.device)
        return (self.states[idx], self.actions[idx], self.rewards[idx],
                self.next_states[idx], self.dones[idx])

    def __len__(self):
        return self.size



epsilon_end = 0.05
epsilon_decay = 50_000

class Agent:
    def __init__(self, input_size, n_actions, learning_rate=0.001, gamma=0.99,
                 batch_size=64, buffer_size=50000, epsilon_start=1.0):
        self.epsilon_start = epsilon_start
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.n_actions = n_actions

        self.model = DQN(input_size, n_actions).to(self.device)
        self.target_model = DQN(input_size, n_actions).to(self.device)

        self.target_update = 500
        self.target_model.load_state_dict(self.model.state_dict())

        self.target_model.eval()

        self.optimizer=optim.Adam(self.model.parameters(), lr=learning_rate)

        self.loss_function = nn.SmoothL1Loss()

        self.environment_steps = 0

        self.memory = ReplayBuffer(
            capacity=buffer_size,
            state_size=input_size,
            device=self.device
        )

        self.gamma=gamma

        self.batch_size=batch_size

        self.steps=0

    def choose_action(self, state, greedy=False):
        if not greedy:
            self.environment_steps += 1
            if random.random() < self.get_epsilon():
                return random.randrange(self.n_actions)

        state = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.inference_mode():
            q_values = self.model(state)
        return q_values.argmax(dim=1).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.add(state, action, reward, next_state, done)

    def training_step(self):
        if len(self.memory) < self.batch_size:
            return None

        states, actions, rewards, next_states, dones = (
            self.memory.sample(self.batch_size)
        )


        current_q = self.model(states).gather(
            1, actions.unsqueeze(1)
        ).squeeze(1)

        with torch.no_grad():
            next_actions = self.model(next_states).argmax(
                dim=1, keepdim=True
            )

            next_q = self.target_model(next_states).gather(
                1, next_actions
            ).squeeze(1)

            target_q = rewards + self.gamma * next_q * (1 - dones)

        loss = self.loss_function(current_q, target_q)

        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()

        #torch.nn.utils.clip_grad_norm_(self.model.parameters(), 10.0)

        self.optimizer.step()

        self.steps += 1

        if self.steps % self.target_update == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        return loss.detach()

    def get_epsilon(self):
        return epsilon_end + (
                self.epsilon_start - epsilon_end
        ) * np.exp(-self.environment_steps / epsilon_decay)