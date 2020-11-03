from deck import Deck


import random
from deck import Deck
from hand_5 import Hand_5
from itertools import combinations
import random_functions as r_f

# Todo: - pour l'implémentation des différents pots
#       idée: amount to call est une liste qui correspond à chaque pot. Les pots sont ordonnés
#       par ordre croissant de amount_to_call. Lorsqu'un nouveau joueur se met tapis, on crée
#       un nouveau pot associé à la valeur du tapis, et on update le pot consécutif
#       (avec un amount_to_call juste supérieur), aussi, les joueurs associés à ce pot
#       sont les joueurs du pot suivant + le joueur qui a fait tapis.
#       On ajoute le joueur qui a fait tapis à tous les pots qui ont un amount_to_call
#       moins important. (C'est pas clair mais je me comprends)
#       - dans la méthode set(), s'occuper des cas où il ne reste plus qu'un active_player car tous les autres
#       se sont couchés, et des cas où il ne reste plus qu'un active_player car certains ont fait tapis. Premier cas:
#       il faut donner tout le pot à celui qui reste sans finir la partie. Deuxieme cas: il faut finir la partie
#       (dévoiler toutes les cartes) et appeler give_pots().



class Table:

    def __init__(self, table_players, small_blind, big_blind, dealer="random", mode="high", limit="no-limit",
                 coin_stacks="default", max_reraise=float("inf")):
        self.nb_players = len(table_players)
        self.players = table_players
        self.nb_players = len(self.players)
        if dealer == "random":
            self.id_dealer = random.randint(0, self.nb_players - 1)
        else:
            self.id_dealer = dealer
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.active_players = [True for _ in range(self.nb_players)]
        self.sb = small_blind
        self.bb = big_blind
        self.deck = Deck()
        self.cards = []
        self.pots = [0]
        self.players_in_pots = [list(range(self.nb_players))]
        self.id_dealer = 0  # l'indice du dealer
        self.last_raiser = 0

    def __iter__(self):
        id_player = self.id_speaker
        for i in range(sum(self.active_players)):
            yield self.players[id_player]
            id_player = self.next_player_id(id_player)

    def new_set(self):
        for player in self.players:
            player.hand = []
            player.is_all_in = False
            player.final_hand = None  ### RODRIGUE ###
        self.id_dealer = (self.id_dealer + 1) % self.nb_players
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.pots = [0]
        self.players_in_pots = [list(range(self.nb_players))]
        self.cards = []
        self.deck = Deck()

    def next_player_id(self, player_id, step=1):
        next_id = (player_id + step) % self.nb_players
        while not self.active_players[next_id]:
            next_id = (next_id + step) % self.nb_players
        return next_id

    def initialise_round(self):
        self.manage_pots()
        for player in self.players:
            player.on_going_bet = 0
        self.id_speaker = self.next_player_id(self.id_dealer)

    def set(self):
        self.new_set()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            round_ob()
            if sum(self.active_players) == 1:
                break
        self.give_pots()

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            blind = [self.sb, self.bb][i]
            print(f"{self.players[self.id_speaker].name} bets {blind}")
            self.players[self.id_speaker].put_on_going_bet(blind)
            self.last_raiser = self.id_speaker
            self.id_speaker = self.next_player_id(self.id_speaker)

    def pre_flop(self):
        print(f'Dealer : {self.id_dealer}', f"Speaker : {self.id_speaker}", sep='\n')
        self.deal_and_blinds()
        return self.players_speak(self.bb)

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for _ in range(3)]
        print([str(card) for card in self.cards])
        return self.players_speak()

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        return self.players_speak()

    def manage_pots(self):
        ogb_values = [0] + list(set([player.on_going_bet for player in self.players if not player.is_folded]))
        # on met le 0 pour la ligne 18, pour le ogb_values[i-1]
        for i in range(1, len(ogb_values)):
            pot_value = 0
            pot_players = []
            for p_id in range(self.nb_players):
                player_ogb = self.players[p_id].on_going_bet
                if player_ogb >= ogb_values[i - 1]:  #
                    pot_value += min(player_ogb - ogb_values[i - 1], ogb_values[i] - ogb_values[i - 1])
                    # importance du min : si l'ogb du joueur se situe entre deux ogb_values => le joueur s'est couché
                if player_ogb >= ogb_values[i]:
                    pot_players.append(p_id)
            self.pots.append((pot_value, pot_players))

    def players_speak(self, mise=0, raiser=None):
        for active_player in self:
            if active_player == raiser:
                return
            player_id = self.id_speaker
            action, amount = active_player.speaks(mise)
            self.id_speaker = self.next_player_id(self.id_speaker)  # on passe mtn au prochain en cas de raise
            if action == 'r':
                self.players_speak_ro(amount, raiser=active_player)
            if action == 'f':
                self.active_players[player_id] = False

    def rank_hands(self):
        """ Renvoie un dictionnaire avec, pour chaque indice de joueur, le rang de sa main parmi tous les joueurs.
        On fait ça pour gérer les cas d'égalité"""
        players_hands = [None] * self.nb_players
        for player_id in range(self.nb_players):
            player = self.players[player_id]
            remaining_players = self.pots[0][1]  # la liste des INDICES des joueurs participant au premier pot
                                                            # (les pots étant ordonnés en pyramide)
            if player_id in remaining_players:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.cards, 5)]
                players_hands[player_id] = player.final_hand = max(possible_hands)

        ranked_hands = r_f.rank_dict(players_hands)
        return ranked_hands


    def give_pots(self):
        """Répartit chaque pot à ses vainqueurs"""
        ranked_hands = self.rank_hands()  # un dictionnaire avec pour chaque player_id, son rang sur la table
        for pot in self.pots:
            pot_players = pot[1]  # les joueurs qui participent à ce pot
            pot_winners = r_f.maxes(pot_players, key=lambda p_id: ranked_hands[p_id])
            for player_id in pot_winners:
                n = len(pot_winners)
                self.players[player_id].stack += round(pot[0] / n)  ### voir plus tard le cas où ce n'est pas un entier
