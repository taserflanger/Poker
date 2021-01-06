import random
from typing import List

from deck import Deck
from hand_5 import Hand_5
from itertools import combinations
import utils
from player import Player


class Table:

    def __init__(self,
                 table_players: List[Player],
                 small_blind: int,
                 big_blind: int,
                 id_dealer="random",
                 verbose=True):
        self.nb_players = len(table_players)
        self.players = table_players
        self.nb_players = len(self.players)
        self.give_players_ids()
        if id_dealer == "random":
            self.dealer = self.players[random.randint(0, self.nb_players - 1)]
        else:
            self.dealer = self.players[id_dealer]
        self.speaker = self.next_player(self.dealer)
        self.sb = small_blind
        self.bb = big_blind
        self.deck = Deck()
        self.cards = []
        self.pots = []
        self.history = []
        self.verbose = verbose

        # rajouter les joueurs à la table
        for p in self.players:
            p.table = self

    def __iter__(self):
        """Parcourt tous les joueurs de la table, à partir du speaker."""
        speaker_id = self.speaker.id
        for player in self.players[speaker_id:] + self.players[:speaker_id]:
            yield player

    def print(self, *values, sep=..., end=..., file=..., flush=...):
        if self.verbose:
            print(*values, sep, end, file, flush)

    def give_players_ids(self):
        i = 0
        for player in self.players:
            player.id = i
            i += 1

    def set_up_game(self):

        for player in self.players:
            player.hand = []
            player.is_all_in = player.is_folded = False
            if player.stack == 0:
                player.is_folded = True
            player.final_hand = None
        self.dealer = self.next_player(self.dealer)
        while self.dealer.is_folded:
            self.dealer = self.next_player(self.dealer)
        self.print(f"Dealer is {self.dealer.name}")
        self.speaker = self.next_player(self.speaker)  # ?? je ne comprends pas ça
        self.pots = []
        self.cards = []
        if len(self.deck) < self.nb_players * 2 + 5:
            # on remélange tout le paquet lorsque le paquet précédent est fini
            # ou pas assez de cartes restantes
            self.deck = Deck()

    def next_player(self, player: Player):
        return self.players[(player.id + 1) % self.nb_players]

    def initialise_round(self):
        for player in self.players:
            player.on_going_bet = 0
        self.speaker = self.next_player(self.dealer)

    def game(self):
        all_folded = False
        self.set_up_game()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            round_ob()
            self.manage_pots()
            if self.folded_players() == self.nb_players - 1:
                all_folded = True
                break
        self.give_pots(all_folded)

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            blind_amount = [self.sb, self.bb][i]
            self.speaker.speaks(blind_amount, blind=True)
            self.history.append(
                (self.distance_to_dealer(self.speaker),
                 0, blind_amount, 0,
                 -1)
            )
            self.speaker = self.next_player(self.speaker)

    def pre_flop(self):
        self.print(f'Dealer : {self.dealer.name}')
        self.deal_and_blinds()
        self.players_speak(self.bb)

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for _ in range(3)]
        self.print(" -".join([str(card) for card in self.cards]))
        self.players_speak()

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        self.print(" -".join([str(card) for card in self.cards]))
        self.players_speak()

    def players_speak(self, mise=0, raiser=None):
        for player in self:
            if self.active_players() == 1:
                return
            if player == raiser or player.is_all_in or player.is_folded:
                continue
            action, amount, decision_time = player.speaks(mise)
            self.history.append(
                (self.distance_to_dealer(player),
                 ["r", "c", "f"].index(action),
                 amount,
                 decision_time,
                 player.get_current_best_hand())
            )
            amount_to_call = self.speaker.on_going_bet
            self.speaker = self.next_player(self.speaker)  # on passe mtn au prochain en cas de raise
            if action == 'r':
                return self.players_speak(amount_to_call, raiser=player)

    def distance_to_dealer(self, player):
        d = 0
        i = self.players.index(player)
        while self.players[i] != self.dealer:
            i = (i + 1) % self.nb_players
            d += 1
        return d

    def active_players(self):
        return sum([True for player in self.players if not (player.is_folded or player.is_all_in)])

    def folded_players(self):
        return sum([True for player in self.players if player.is_folded])

    def manage_pots(self):
        ogb_values = [0] + list(set([player.on_going_bet for player in self.players if not player.is_folded]))
        # on met le 0 pour la ligne 18, pour le ogb_values[i-1]
        if ogb_values[1] > 0:  # dans le cas où tout le monde a check, on ne crée pas de pot -> gain de temps
            for i in range(1, len(ogb_values)):
                pot_value = 0
                pot_players = []
                for player in self.players:
                    if player.on_going_bet >= ogb_values[i - 1]:
                        pot_value += min(player.on_going_bet - ogb_values[i - 1], ogb_values[i] - ogb_values[i - 1])
                        # importance du min : si l'ogb du joueur se situe entre deux ogb_values = le joueur s'est couché
                    if player.on_going_bet >= ogb_values[i]:
                        pot_players.append(player)
                self.pots.append((pot_value, pot_players))

    def get_final_hands(self):
        """ Assigne à chaque joueur non couché sa main finale, c'est à dire sa meilleure combinaison de 5 cartes"""
        for player in self.players:
            if not player.is_folded:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.hand, 5)]
                player.final_hand = max(possible_hands)

    def get_winners(self, players):
        """Prend une liste de joueurs en entrée, renvoie les vainqueurs (meilleures mains finales)"""
        players_hands = [(player.final_hand, player) for player in players if not player.is_folded]
        winners = utils.maxes(players_hands, key=lambda players_hand: players_hand[0])  # max selon la main du joueur
        return [pot_winner[1] for pot_winner in winners]

    def give_pots(self, all_folded=False):
        """Répartit chaque pot à ses vainqueurs"""
        if all_folded:
            winner = [player for player in self.players if not player.is_folded][0]
            self.print(f"Everyone folded, {winner} wins {sum(v for v, _ in self.pots)}")
        else:
            self.get_final_hands()
        for pot_value, pot_players in self.pots:
            if all_folded:
                winner.stack += pot_value
                continue
            pot_winners = self.get_winners(pot_players)
            n = len(pot_winners)
            for player in pot_winners:
                value_for_player = pot_value // n  # au cas où le pot n'est pas divisible par n
                self.print(f"{player.name} wins {pot_value}")
                player.stack += value_for_player
                pot_value -= value_for_player
                n -= 1
