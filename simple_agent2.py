from agent import Agent

class Agent2(Agent):

    def __init__(self):
        super(Agent2, self).__init__()

    def learn(self, score_delta):
        pass

    def get_action(self, observation):
        return self.HEADS
