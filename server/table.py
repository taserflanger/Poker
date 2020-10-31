"""
L'itérateur de la classe table permet de parcourir les joueurs restant dans la main, à partir de celui qui doit parler
en premier.
Pour jouer une main:

TODO:   - s'occuper de la fonctionnalité fold, et de l'attribut ind_speaker
        - s'occuper du cas de figure ou tout le monde sauf 1 s'est couché
        - retranscrire dans un modèle client/serveur, où le client n'a accès qu'aux informations qui le concernent
        - (détail: Si un joueur n'a pas assez d'argent pour faire sa blinde, il doit être exclu au début)

"""
import random
from deck import Deck
from hand_5 import Hand_5  ### RODRIGUE ###
from itertools import combinations  ### RODRIGUE ### pour les combinaisons possibles de mains de 5 cartes
import random_functions as r_f

class Table:

    def __init__(self, table_players, small_blind, big_blind, dealer="random"):
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
        self.id_dealer = 0  # l'indice du dealer

    def __iter__(self):
        yield self.players[self.id_speaker]
        for i in range(sum(self.active_players) - 1):
            yield self.next_player_id()

        i = (self.id_dealer + 1) % self.nb_players
        for k in range(self.nb_players):
            yield (i + k) % self.nb_players

    def new_set(self):
        for player in self.players:
            player.hand = []
            player.final_hand = None  ### RODRIGUE ###
        self.id_dealer = (self.id_dealer + 1) % self.nb_players
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.pots = [0]
        self.cards = []
        self.deck = Deck()

    def next_player_id(self, player_id):
        next_id = (player_id + 1) % self.nb_players
        while not self.active_players[next_id]:
            next_id = (next_id + 1) % self.nb_players
        return next_id

    def initialise_round(self):
        for player in self.players:
            self.pots[0] += player.on_going_bet  ### A REVOIR EN PRENANT EN COMPTE LES SIDE POTS
            player.on_going_bet = 0
        self.id_speaker = self.next_player_id(self.id_dealer)

    def set(self):
        self.new_set()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            round_ob()
            if sum(self.active_players) == 1:
                self.get_winner()  # le cas où tout le monde s'est couché ou a fait tapis
        if sum(self.active_players) > 1:
            self.get_winner()

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            print(f"{self.players[self.id_speaker].name} bets {[self.sb, self.bb][i]}")
            self.players[self.id_speaker].on_going_bet += [self.sb, self.bb][i]
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


    def players_speak(self, mise=0):
        # Todo: implémenter le tour depuis le raiser
        for _ in range(self.nb_players):
            speaker = self.id_speaker
            dealer = self.id_dealer

            if sum(self.active_players) == 1:
                winner_id = self.next_player_id(
                    speaker)  # on trouve le dernier joueur restant (qui est aussi le suivant)
                return winner_id
            if not self.active_players[speaker]:
                continue

            action, amount = self.players[speaker].speaks(mise)
            if speaker == dealer and self.players[self.next_player_id(dealer)].on_going_bet == mise:
                # si personne n'a relancé dans le tour, on passe à l'étape suivante.
                return
            if action == "f":
                self.active_players[speaker] = False
            self.id_speaker = self.next_player_id(self.id_speaker)
            mise += amount

    def get_winner(self):
        """
        TODO: la fonction doit faire une liste ordonnée par ordre décroissant de valeur les mains
            des joueurs. Ensuite, en bouclant sur chaque pot, elle doit attribuer à chaque fois le pot au meilleur
            joueur de ce pot. Dans cette étape, elle doit prendre en considération des éventuelles égalités.

        """
        players_hands = [None] * self.nb_players
        for player_id in range(self.nb_players):
            player = self.players[player_id]
            if self.active_players[player_id]:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.cards, 5)]
                player.final_hand = max(possible_hands)
                players_hands.append(player.final_hand)
        winning_hand, winners_ids = r_f.max_with_ids(players_hands)
        return winning_hand, winners_ids
