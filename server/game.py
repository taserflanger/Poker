from random import randint


class Game:
    def __init__(self, nb_players=5, sm_blind=10, mode="high", limit="no-limit", dealer="random",
                 coin_stacks="default"):
        """
        :param nb_players: int
        :param sm_blind: int
        :param mode: "high" | "low" | "high/low"
        :param limit: "limit" | "pot-limit" | "no-limit"
        :param dealer: "random" | [0 : nb_players-1]
        """

        # initialisations
        self.nb_players = nb_players
        self.sm_blind = sm_blind
        self._mode = mode
        self._limit = limit
        self.round = 1
        self.game_state = "preflop"
        self.pot = 0
        self.tmp_stacks = [0 for _ in range(self.nb_players)]

        # initialisation des jetons de chaque joueurs
        if coin_stacks == "default":
            self.coin_stacks = [self.sm_blind * 100 for _ in range(self.nb_players)]
        else:
            self.coin_stacks = coin_stacks

        # choix du dealer (custom ou random)
        if dealer == "random":
            self.dealer = randint(0, self.nb_players - 1)
        else:
            self.dealer = dealer

        # le premier joueur est le joueur à gauche du dealer
        # (les joueurs sont disposés dans le sens trigo par rapport à la numérotation)
        self.current_player = (self.dealer + 1) % self.nb_players

    def place_to_tmp(self, player, amount):
        """
        Place une quantité de jetons *amount* sur le stack temporaire du joueur *player*.
        :param player:
        :param amount:
        :return:
        """
        #TODO: vérifier qu'il y a assez d'argent
        self.tmp_stacks[player] += amount
        self.coin_stacks[player] -= amount

    def iterate(self):
        # Avant le flop
        p = self.current_player
        N = self.nb_players
        if game_state=="preflop":
            # small et big blindes
            d = (p - self.dealer) % N
            if d==1:
                self.place_to_tmp(p, self.sm_blind)
                return
            if d==2:
                self.place_to_tmp(p, self.sm_blind)
                return
            # ici implémenter les différentes possibilités (il va y avoir du code en commun avec des possibilités
            # à l'extérieur du préflop): call, raise, fold