from agent import Agent
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense
from keras.initializers import TruncatedNormal
from keras.optimizers import SGD

class QLearning_Agent2(Agent):

    def __init__(self):
        super(QLearning_Agent2, self).__init__()
        self.ACTIONS = 3
        self.GAMMA = 0.9
        self.OBSERVE = 5000
        self.EPSILON = .005
        self.REPLAY_MEMORY = 5000
        self.BATCH = 10
        self.INPUT_DIM = 2
        self.LEARNING_RATE = .2
        self.observation = None
        self.memory = []
        self.create_model()

    def create_model(self):
        model = Sequential()
        model.add(Dense(12, kernel_initializer=TruncatedNormal(mean=0.0, stddev=0.01), activation='relu', input_shape = (self.INPUT_DIM,)))
        model.add(Dense(8, kernel_initializer=TruncatedNormal(mean=0.0, stddev=0.01), activation='relu'))
        model.add(Dense(self.ACTIONS, kernel_initializer=TruncatedNormal(mean=0.0, stddev=0.01), activation='sigmoid'))
        model.compile(loss='categorical_crossentropy', optimizer=SGD(lr=self.LEARNING_RATE), metrics=['accuracy'])
        self.model = model

    def get_random_action(self):
        actions = np.zeros(self.ACTIONS)
        actions[random.randrange(self.ACTIONS)] = 1
        action = np.argmax(actions)
        return action

    def get_batch(self):
        batch_size = self.BATCH
        if len(self.memory) < batch_size:
            return []
        samples = np.array(random.sample(self.memory, batch_size))
        S = samples[:, 0 : self.INPUT_DIM]
        a = samples[:, self.INPUT_DIM]
        r = samples[:, self.INPUT_DIM + 1]
        S_prime = samples[:, self.INPUT_DIM + 2 : 2 * self.INPUT_DIM + 2]

        r = r.repeat(self.ACTIONS).reshape((batch_size, self.ACTIONS))

        #S = S.reshape((batch_size, ) + self.INPUT_DIM)
        #S_prime = S_prime.reshape((batch_size, ) + self.INPUT_DIM)

        X = np.concatenate([S, S_prime], axis=0)
        Y = self.model.predict(X)

        #print(S)
        #print(a)
        #print(r)
        #print(S_prime)
        #print(X)
        #print(X.shape)
        #print(Y)
        #print(Y.shape)

        Qsa = np.max(Y[batch_size:], axis=1).repeat(self.ACTIONS).reshape((batch_size, self.ACTIONS))
        delta = np.zeros((batch_size, self.ACTIONS))
        a = np.cast['int'](a)
        delta[np.arange(batch_size), a] = 1
        targets = (1 - delta) * Y[:batch_size] + delta * (r + self.GAMMA * Qsa)
        return S, targets

    def learn(self, prev_total_score, action_taken_by_this_agent, score_delta):
        self.action = action_taken_by_this_agent
        self.reward = score_delta
        batch = self.get_batch()
        if (len(batch) > 0):
            inputs, targets = batch
            self.model.train_on_batch(inputs, targets)

    def get_action(self, observation):

        if self.observation != None:
            self.last_observation = self.observation
            self.memory.append(np.concatenate([self.last_observation, [self.action], [self.reward], observation]))
            if self.REPLAY_MEMORY > 0 and len(self.memory) > self.REPLAY_MEMORY:
                self.memory.pop(0)

        self.observation = observation

        if random.random() < self.EPSILON:
            action = self.get_random_action()
        else:
            q = self.model.predict(np.array(observation).reshape(-1, len(observation)))
            action = int(np.argmax(q[0]))

        return action

# agent1: observation = [total_score, heads_or_tails]
# agent2: observation = [total_score, keep_or_give]

# experiment_replay = (observation, action_taken_by_this_agent, score_delta, next_observation)

