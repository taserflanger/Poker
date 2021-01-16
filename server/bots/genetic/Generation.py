from typing import Union, List

import numpy as np
from nptyping import NDArray

from . import BotGenetic


class Generation:
    def __init__(self, mutation_factor: float,
                 sizes: List[int],
                 W: Union[str, List[NDArray]] = "random",
                 b: Union[str, List[NDArray]] = "random",
                 f: Union[str, List[NDArray]] = "random", ):
        """
        Génération de bots qui mutent autour de gênes communs

        :param mutation_factor: facteur de mutation
        :param sizes: taille des couches intermédiaires
        :param W: poids synaptiques de référence
        :param b: biais synaptique de référence
        :param f: fonction de transfert d’histoire de référence
        """
        self.ref_W = W
        self.ref_b = b
        self.ref_f = f
        self.sizes = sizes
        self.alpha = mutation_factor

    def generate_bot_pool(self, size: int, stacks: List[int]):
        W = self.ref_W
        b = self.ref_b
        f = self.ref_f
        nb_layers = len(W)
        for i in range(size):
            if self.ref_W != "random":
                W = [self.ref_W[j] + (2 * np.random.random(np.shape(self.ref_W[j])) - 1) * self.alpha
                     for j in range(nb_layers)]
            if self.ref_b != "random":
                b = [self.ref_b[j] + (2 * np.random.random(np.shape(self.ref_b[j])) - 1) * self.alpha
                     for j in range(nb_layers)]
            if self.ref_f != "random":
                f = [self.ref_f[j] + (2 * np.random.random(np.shape(self.ref_f[j])) - 1) * self.alpha
                     for j in range(len(self.ref_f))]

            yield BotGenetic(f"bot{i}", stacks[i], self.sizes, W, b, f)
