from deck import Deck

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
        self.pot = 0
        self.id_dealer = 0  # l'indice du dealer
        self.last_raiser = 0

    def __iter__(self):
        i = (self.id_dealer + 1) % self.nb_players
        for k in range(self.nb_players):
            yield (i + k) % self.nb_players

    def new_set(self):
        for player in self.players:
            player.hand = []
            player.is_all_in = False
            player.final_hand = None  ### RODRIGUE ###
        self.id_dealer = (self.id_dealer + 1) % self.nb_players
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.pot = 0
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
            winner_id = round_ob()
            if winner_id:  # s'il n'y a pas de winner_id, c'est que personne n'a gagné et on continue
                break
        print(f"{self.players[winner_id].name} wins")

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

            action, amount = self.players[self.id_speaker].speaks(amount_to_call)

            if action == "f":
                self.active_players[speaker] = False
            elif action == "r":
                self.last_raiser = speaker
            self.id_speaker = self.next_player_id(self.id_speaker)

            ######### POUR DETERMINER LA MEILLEURE MAIN DE LA TABLE #########


### RODRIGUE

    def get_winner(self):
        players_hands = [None] * self.nb_players
        for player_id in range(self.nb_players):
            player = self.players[player_id]
            if self.active_players[player_id]:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.cards, 5)]
                player.final_hand = max(possible_hands)
                players_hands.append(player.final_hand)
        winning_hand, winners_ids = r_f.max_with_ids(players_hands)
        return winning_hand, winners_ids

