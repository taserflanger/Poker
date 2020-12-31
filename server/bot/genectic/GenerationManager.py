from typing import List, Union
import os

import numpy as np
from nptyping import NDArray

from bot.genectic.Bot import Bot
from bot.genectic.Generation import Generation
from table import Table


class GenerationManager:
    def __init__(self,
                 sizes: List[int],
                 mutation_factor: float = 10,
                 W: Union[str, List[NDArray]] = "random",
                 b: Union[str, List[NDArray]] = "random",
                 f: Union[str, List[NDArray]] = "random"):
        """
        Classe pour entraîner l’algorithme génétique en jouant contre lui-même
        :param sizes: taille des layers cachés dans cerveau des bots
        :param mutation_factor: facteur de mutation
        :param W: poids synaptiques initiaux (random si non spécifié)
        :param b: biais synaptiques initiax (random si non spécifié)
        :param f: fonction de transfert d’éléments d’histoire (random si non sécifié)
        """
        self.MUTATION_FACTOR = mutation_factor
        self.sizes = sizes
        self.current_generation = Generation(mutation_factor=0.1, sizes=self.sizes, W=W, b=b, f=f)

    def train(self,
              N: int, m: int,
              nb_players: int,
              small_blind: int = 5,
              max_round: int = 1000) \
            -> (NDArray, NDArray, NDArray):
        """
        Entraîne le modèle
        :param N: nombre de générations
        :param m: nombre de parties jouées par génération
        :param nb_players: nombre de joueurs par table
        :param small_blind: valeur de la petite blinde
        :param max_round: nombre maximal de tours avant la fin d’une partie
        :return: W, b, f trained
        """

        scores = np.ndarray((nb_players,))

        for g in range(N):
            bots = []
            os.system('cls')
            print("*" * (g * 50 // N), f"generation {g}")
            for game in range(m):
                stacks = [100 for _ in range(nb_players)]
                # TODO rajouter la possibilité de faire des staccks random
                bots: List[Bot] = list(self.current_generation.generate_bot_pool(nb_players, stacks))
                table = Table(
                    table_players=bots,
                    small_blind=small_blind,
                    big_blind=2 * small_blind)
                for _ in range(max_round):
                    table.game()
                    # si un joueur ruine tous les autres, on arrête la partie
                    if sum([b.stack > 0 for b in bots]) == 1:
                        break
                scores += np.array([b.stack for b in bots])
            scores /= m

            winner = bots[scores.argmax()]
            # la nouvelle génération a comme poids de référence ceux du winner
            self.current_generation = Generation(self.MUTATION_FACTOR, self.sizes, winner.W, winner.b, winner.f)

        return self.current_generation.ref_W, self.current_generation.ref_b, self.current_generation.ref_f
