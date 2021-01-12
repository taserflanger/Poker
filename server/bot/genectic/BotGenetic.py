from typing import List, Union
import numpy as np
from nptyping import NDArray
from server.utils import softmax, relu
from time import time

from ..Bot import Bot


class BotGenetic(Bot):
    def __init__(self, player_name: str,
                 player_stack: int,
                 sizes: List[int],
                 W: Union[str, List[NDArray]] = "random",
                 b: Union[str, List[NDArray]] = "random",
                 f: Union[str, List[NDArray]] = "random"):
        """
        bot dont les paramètres du réseau de neurones se modifient génétiquement
        :param player_name: nom du bot
        :param sizes: tailles des layers
        :param W: weights (doivent être dans les bonnes dimensions par rapport à sizes)
        :param b: biases (idem)
        :param f: fonction de morph des unités d’histoire
        """
        super().__init__(player_name, player_stack)
        self.sizes = [5] + sizes + [4]
        self.nb_layers = len(self.sizes)
        self.W = [np.random.randn(self.sizes[k - 1], self.sizes[k]) for k in
                  range(self.nb_layers)] if W == "random" else W
        self.b = [np.random.randn(self.sizes[k]) for k in range(self.nb_layers)] if b == "random" else b
        self.L = [np.zeros((self.sizes[k])) for k in range(self.nb_layers)]
        self.f = [np.random.randn(self.sizes[0], self.sizes[1]) for _ in range(4)] if f == "random" else f

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
        metaW = [self.W[1]]*len(history)
        # for i in range(len(history) - 1):
        #     metaW = list(map(self.history_mapper, metaW))
        #     # TODO: Cette opération prend beacoup trop de temps. calculer une fois le mapping au
        #     #  début puis tronquer selon le nombre nécessaire
        #     metaW.append(self.W[1])
        W1 = np.concatenate(metaW)
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
        self.calculate_first_layer(np.array(list(history)))
        for k in range(2, self.nb_layers-1):
            self.calculate_hidden_layer(k)
        self.calculate_last_layer()

    def speaks(self, amount_to_call, blind=False):
        bet = amount_to_call - self.on_going_bet  # on initialise à la valeur du call
        a = time()
        player_action = self.ask_action(bet, blind)
        decision_time = time() - a
        # on calcule le temps de décision car ask_action est implémenté sans timer pour les bots
        if player_action == 'c' or blind:
            bet = self.calls(bet)
        if player_action == 'r':
            a = time()
            bet, player_action = self.ask_amount(bet)
            decision_time += time() - a
        if player_action == 'f':
            self.is_folded = True
            bet = 0
        self.finalize_action(bet, blind, player_action)
        return player_action, bet, decision_time

    def finalize_action(self, bet, blind, player_action):
        self.stack -= bet
        self.on_going_bet += bet
        if self.stack == 0:
            self.is_all_in = True
        self.print_action(player_action, bet, blind)

    def ask_action(self, bet, blind):
        if blind:
            return "c"
        else:
            self.forward_propagate(reversed(self.table.history))
            action_layer = self.L[-1][1:]
            # TODO ajouter un moyen virtuel à un bot de pouvoir jouer sur le temps de réponse
            # à priori tant qu’on ne le fait pas jouer contre des gens chez qui l’influence du temps
            # compte, ça na marchera pas
            action = ["f", "c", "r"][action_layer.argmax()]
            if action == "r" and self.stack <= bet:
                action = "c"
            if action == "f":
                self.is_folded = True
            return action

    def ask_amount(self, bet):
        # pas besoin de recalculer le dernier layer vu qu’on demande toujours
        # la donnée de amount après avoir demandé l’action
        return max(bet+1, min(self.stack, self.L[-1][0])), "r"
