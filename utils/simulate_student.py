import numpy as np


class SimulateStudent(object):
    def __init__(self, pi, A, B):
        self.priors = pi
        self.states_name = ["Learned", "Not learned"]
        self.transition = A
        self.emission = B

    def random_MN_draw(self, n, probs):
        """ get X random draws from the multinomial distribution whose probability is given by 'probs' """
        mn_draw = np.random.multinomial(n,probs) # do 1 multinomial experiment with the given probs with probs= [0.5,0.5], this is a coin-flip
        return np.where(mn_draw == 1)[0][0] # get the index of the state drawn e.g. 0, 1, etc.

    def simulate(self, nSteps):
        """ given an HMM = (A, B, pi), simulate state and observation sequences """
        observations = np.zeros(nSteps, dtype=np.int) # array of zeros
        states = np.zeros(nSteps, dtype=np.int)
        states[0] = self.random_MN_draw(1, self.priors) # appoint the first state from the prior dist
        observations[0] = self.random_MN_draw(1, self.emission[states[0]]) # given current state t, pick what row of the B matrix to use

        for t in range(1, nSteps): # loop through t
            states[t] = self.random_MN_draw(1, self.transition[states[t-1]]) # given prev state (t-1) pick what row of the A matrix to use
            observations[t] = self.random_MN_draw(1, self.emission[states[t]]) # given current state t, pick what row of the B matrix to use

        return observations, states
