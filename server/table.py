"""
L'itérateur de la classe table permet de parcourir les joueurs restant dans la main, à partir de celui qui doit parler
en premier.
Pour jouer une main:

TODO:   - retranscrire dans un modèle client/serveur, où le client n'a accès qu'aux informations qui le concernent
        - (détail: Si un joueur n'a pas assez d'argent pour faire sa blinde, il doit être exclu au début)

"""
import random
from deck import Deck
from hand_5 import Hand_5  ### RODRIGUE ###
from itertools import combinations  ### RODRIGUE ### pour les combinaisons possibles de mains de 5 cartes
import random_functions as r_f
from pots import Pots


# Todo: pour l'implémentation des différents pots
#       idée: amount to call est une liste qui correspond à chaque pot. Les pots sont ordonnés
#       par ordre croissant de amount_to_call. Lorsqu'un nouveau joueur se met tapis, on crée
#       un nouveau pot associé à la valeur du tapis, et on update le pot consécutif
#       (avec un amount_to_call juste supérieur), aussi, les joueurs associés à ce pot
#       sont les joueurs du pot suivant + le joueur qui a fait tapis.
#       On ajoute le joueur qui a fait tapis à tous les pots qui ont un amount_to_call
#       moins important. (C'est pas clair mais je me comprends)

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
        self.nb_players_remaining = self.nb_players
        self.sb = small_blind
        self.bb = big_blind
        self.deck = Deck()
        self.cards = []
        self.pots = Pots()
        self.final_pots = []
        self.id_dealer = 0  # l'indice du dealer
        self.last_raiser = 0

    def __iter__(self):
        yield self.players[self.id_speaker]
        for i in range(self.nb_players_remaining - 1):
            yield self.next_player_id()

    def new_set(self):
        for player in self.players:
            player.hand = []
            player.is_all_in = False
            player.final_hand = None  ### RODRIGUE ###
        self.id_dealer = (self.id_dealer + 1) % self.nb_players
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.pots = Pots()
        self.cards = []
        self.deck = Deck()

    def next_player_id(self, player_id, step=1, allow_all_in=False):
        next_id = (player_id + step) % self.nb_players
        while self.players[next_id].folded or (self.players[next_id].is_all_in or allow_all_in):
            next_id = (next_id + step) % self.nb_players
        return next_id

    def initialise_round(self):
        for player in self.players:
            self.pots = Pots()
            player.on_going_bet = 0
        self.id_speaker = self.next_player_id(self.id_dealer)

    def set(self):
        self.new_set()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            round_ob()
            self.pots.calculate()
            print(self.pots)
            self.final_pots.append(self.pots)
            if self.nb_players_remaining == 1:  # le cas où tout le monde s'est couché ou a fait tapis
                break
        self.get_winner()

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            blind = [self.sb, self.bb][i]
            print(f"{self.players[self.id_speaker].name} bets {blind}")
            self.players[self.id_speaker].put_on_going_bet(blind)
            self.pots.create_pot(self.players[self.id_speaker], blind)
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
                self.players[player_id].folded = True

    def players_speak(self):
        while True:
            speaker = self.id_speaker
            next_speaker = self.next_player_id(speaker)
            if self.nb_players_remaining == 1:
                # cas où il ne reste plus qu'un joueur
                winner_id = next_speaker  # on trouve le dernier joueur restant (qui est aussi le suivant)
                return winner_id
            if self.players[speaker].folded or self.players[speaker].is_all_in:
                # si le joueur est fold on le dégage
                continue

            amount_to_call = self.players[self.last_raiser].on_going_bet

            if speaker == self.last_raiser and \
                    self.players[speaker].on_going_bet == amount_to_call:
                # si personne n'a relancé dans le tour, on passe à l'étape suivante.
                return

            action, amount = self.players[speaker].speaks(amount_to_call)

            if action == "f":
                self.players[speaker].folded = True
                self.nb_players_remaining -= 1
            elif action == "c":
                self.pots.update_player(self.players[speaker], self.players[speaker].on_going_bet)
            elif action == "r":
                self.last_raiser = speaker
                self.pots.create_pot(self.players[speaker], self.players[speaker].on_going_bet)
            elif self.players[speaker].is_all_in:
                self.pots.create_pot(self.players[speaker], self.players[speaker].on_going_bet)
            self.id_speaker = self.next_player_id(self.id_speaker)

    def get_winner(self):
        """
        TODO (roro s'en occupe): la fonction doit faire une liste ordonnée par ordre décroissant de valeur des mains
            des joueurs. Ensuite, en bouclant sur chaque pot, elle doit attribuer à chaque fois le pot au meilleur
            joueur de ce pot. Dans cette étape, elle doit prendre en considération des éventuelles égalités.

        """
        players_hands = [None] * self.nb_players
        for player_id in range(self.nb_players):
            player = self.players[player_id]
            if not player.folded:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.cards, 5)]
                player.final_hand = max(possible_hands)
                players_hands.append(player.final_hand)
        winning_hand, winners_ids = r_f.max_with_ids(players_hands)
        return winning_hand, winners_ids
