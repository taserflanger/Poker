import numpy as np
from bot.genectic.utils import relu, softmax
from player import Player


class Bot(Player):
    def __init__(self, player_name, player_stack, sizes):
        """
        bot dont les paramètres du réseau de neurones se modifient génétiquement
        :param sizes: tailles des layers
        """
        super().__init__(player_name, player_stack)
        self.sizes = [5] + sizes + [4]
        self.nb_layers = len(self.sizes)
        self.W = [np.random.randn(self.sizes[k - 1], self.sizes[k]) for k in range(self.nb_layers)]
        self.b = [np.random.randn(self.sizes[k]) for k in range(self.nb_layers)]
        self.L = [np.zeros((self.sizes[k])) for k in range(self.nb_layers)]
        self.f = np.random.randn(4)

    def calculate_hidden_layer(self, k):
        """
        forward propagation pour 1<k<L (le premier et le dernier layer sont traités à part)
        :param k: 1<k<L
        :return: hidden layer k
        """

        self.L[k] = relu(self.W[k].transpose() @ self.L[k - 1] + self.b[k])

    def history_mapper(self, x):
        """
        creates change between events in history
        :param x: float
        :return: float
        """
        return self.f[0] * x + self.f[1]

    def calculate_first_layer(self, history):
        """
        returns first hidden layer from history
        :param history:
        :return:
        """
        W1 = self.W[1]
        for i in range(len(history) - 1):
            W1 = self.history_mapper(W1)
            W1 = np.concatenate([W1, self.W[1]])
        self.L[1] = W1.transpose() @ history.flatten() + self.b[1]

    def calculate_last_layer(self):
        self.L[-1] = self.W[-1].transpose() @ self.L[-2] + self.b[-1]
        self.L[-1][1:] = softmax(self.L[-1][1:])
        self.L[-1][0] = max(self.L[-1][0], 0)

    def forward_propagate(self, history):
        """
        evaluates neural network with history of games
        :param history:
        :return:
        """
        # calculate the first layer form history
        self.calculate_first_layer(np.array(history))
        for k in range(2, self.nb_layers):
            self.calculate_hidden_layer(k)
        self.calculate_last_layer()

    def ask_action(self, bet, blind, c, player_action, max_time):
        if self.stack > bet:
            return np.random.choice(["f", "c", "r"])
        return np.random.choice(["f", "c"])

    def ask_amount(self, bet, remaining_time):
        return np.ramdom.randint(0, self.stack - bet)
