from deck import Deck


import random
from deck import Deck
from hand_5 import Hand_5  ### RODRIGUE ###
from itertools import combinations  ### RODRIGUE ### pour les combinaisons possibles de mains de 5 cartes
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
#
#
#
#
#


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
        yield self.players[self.id_speaker]
        for i in range(sum(self.active_players) - 1):
            yield self.next_player_id()

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
        for player in self.players:
            self.pot += player.on_going_bet
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
        return self.players_speak()

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


    def new_pot(self, amount):
        pass

    def players_speak_ro(self, mise=0, raiser=None):
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

    def players_speak(self):
        # Todo: implémenter le tour depuis le raiser
        while True:
            speaker = self.id_speaker
            previous_speaker = self.next_player_id(speaker, -1)
            next_speaker = self.next_player_id(speaker)
            if sum(self.active_players) == 1:
                # cas où il ne reste plus qu'un joueur
                winner_id = next_speaker  # on trouve le dernier joueur restant (qui est aussi le suivant)
                return winner_id
            if not self.active_players[speaker] or self.players[speaker].is_all_in:
                # si le joueur est fold on le dégage
                continue
            amount_to_call = self.players[previous_speaker].on_going_bet

            if speaker == self.last_raiser and \
                    self.players[speaker].on_going_bet == amount_to_call:
                # si personne n'a relancé dans le tour, on passe à l'étape suivante.
                return

            action, amount = self.players[speaker].speaks(amount_to_call)
            if self.players[speaker].is_all_in:
                self.new_pot(amount)
            if action == "f":
                self.active_players[speaker] = False
            elif action == "r":
                self.last_raiser = speaker
            self.id_speaker = self.next_player_id(self.id_speaker)

    def rank_hands(self):
        """ Renvoie une liste ordonnée des indices des joueurs par ordre croissant de la valeur de leur main."""
        players_hands = [None] * self.nb_players
        for player_id in range(self.nb_players):
            player = self.players[player_id]
            remaining_players = self.pots[0][1]  # la liste des INDICES des joueurs participant au premier pot
                                                            # (les pots étant ordonnés en pyramide)
            if player_id in remaining_players:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.cards, 5)]
                players_hands[player_id] = player.final_hand = max(possible_hands)

        ranked_hands = r_f.sort_ids(players_hands)
        return ranked_hands


    def give_pots(self):
        """
        Répartit les différents pots aux vainqueurs de chaque pot.
        Ne prend pas encore les égalités entre les mains (ligne 4 pas suffisante)
        """
        ranked_hands = self.rank_hands()
        for pot in self.pots:
            pot_players = pot[1]  # les joueurs qui participent à ce pot
            pot_winners = r_f.maxes(pot_players, key=lambda x: ranked_hands.index(x))
            for player_id in pot_winners:
                n = len(pot_winners)
                self.players[player_id].stack += pot[0] / n  ### voir plus tard le cas où ce n'est pas un entier

