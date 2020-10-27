from random import randint

class Game:
    def __init__(self, nb_players=5, sm_blind=10, mode="high", limit="no-limit", dealer="random",
                 coin_stacks="default", max_reraise=float(inf)):
        """
        :param nb_players: int
        :param sm_blind: int
        :param mode: "high" | "low" | "high/low"
        :param limit: "limit" | "pot-limit" | "no-limit"
        :param dealer: "random" | [0 : nb_players-1]
        :param coin_stacks: "default" | [int] * nb_players
        :param max_reraise: int maximum de relances dans une partie
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
        self.amount_to_call = 0
        self.in_game = [True for _ in range(self.nb_players)]
        self.max_reraise = max_reraise
        self.current_reraise=0

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
        self.distribute_cards()

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

    def ask(self):
        # TODO: mettre un timer qui fold à défaut d'une réponse
        p = self.current_player
        c = "call"
        diff = self.amount_to_call-self.tmp_stacks[p]
        if diff==0:
            c = "check"
        answer = input(f"{c} | raise | fold ? ")
        if answer==c:
            self.place_to_tmp(p, diff)
        elif answer=="fold":
            self.in_game[p]=False
        elif answer=="raise":
            amount = input("amount? ")
            self.place_to_tmp(p, diff+amount)
            self.amount_to_call+=amount
            self.current_reraise+=1
            #TODO: changer les possibilités de raise en fonction
            # de la variante de poker considérée (limit, pot-limit, no-limit)

            #(e.g. en limit, on ne peut raise que de 2*sm_blind ou 4*sm_blind)

    def next_player(self):
        self.current_player = (self.current_player + 1) % self.nb_players


    def iterate(self):
        # Avant le flop
        p = self.current_player
        N = self.nb_players
        d = (p - self.dealer) % N
        if self.game_state == "preflop":
            # small et big blindes
            if d==1:
                self.place_to_tmp(p, self.sm_blind)
                self.next_player()
                return
            if d==2:
                self.place_to_tmp(p, 2*self.sm_blind)
                self.amount_to_call = 2*self.sm_blind
                self.next_player()
                return
        ask(p)
        #Si personne n'a relancé dans le tour, on change de game_state
        if d==0 and self.tmp_stacks[(self.dealer+1)%N]==self.amount_to_call:
            self.next_game_state()
            return

    def next_game_state(self):
        """
        Passe d'un gamestate au suivant et relance une partie si on est arrivé à la fin
        :return:
        """
        if self.game_state == "preflop":
            self.show_flop()
            self.game_state = "flop"
        elif self.game_state == "flop":
            self.show_card()
            self.game_state = "turn"
        elif self.game_state == "turn":
            self.show_card()
            self.game_state = "river"
        elif self.game_state == "river":
            self.distribute_pot_to_winner()
            self.distribute_cards()
            self.dealer = (self.dealer + 1) % N
            self.game_state = "preflop"

        # Mettre les stacks temporaires dans le pot, et réinitialiser certaines variables
        self.pot += sum(self.tmp_stacks)
        self.tmp_stacks = [0 for _ in range(N)]
        self.current_reraise = 0
        self.current_player = (self.dealer + 1) % N

    #TODO distribute_pot_to_winner
    def distribute_pot_to_winner(self):
        pass
    #TODO distribute_cards
    def distribute_cards(self):
        pass
    #TODO show_card
    def show_card(self):
        pass
    def show_flop(self):
        for _ in range(3):
            self.show_card()