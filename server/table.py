import random
import time
from itertools import combinations
from typing import List

from server import server_utils as fs, table_utils as ft
from server import utils
from .deck import Deck
from .hand5 import Hand5
from .player import Player


class Table:

    def __init__(self, table_players: List[Player], small_blind: int, big_blind: int, id_dealer: int = -1,
                 bot_training=True):
        self.nb_players = len(table_players)
        self.players = table_players
        self.nb_players = len(self.players)
        ft.give_players_ids(self)
        if id_dealer == -1:
            # -1: random dealer
            self.dealer = self.players[random.randint(0, self.nb_players - 1)]
        else:
            self.dealer = self.players[id_dealer]
        self.speaker = self.next_player(self.dealer)
        self.sb, self.bb = small_blind, big_blind
        self.deck = Deck()
        self.cards, self.pots, self.final_winners, self.wait_in, self.wait_out = map(list, ([] for _ in range(5)))
        self.final_hand, self.in_change, self.in_game, self.end, self.redistribution = map(bool,
                                                                                           (False for _ in range(5)))
        self.history = []
        if bot_training:
            for p in self.players:
                p.table = self
        self.verbose = not bot_training
        # TODO: fait dans salon.py. Pour train les bots, utiliser l’ancienne version
        # # rajouter les joueurs à la table
        # for p in self.players:
        #     p.table = self

        self.final_hand = self.in_change = self.in_game = self.end = self.redistribution = False
        self.salon = None

    # ********************** OPERATIONS ***********************:
    def __iter__(self):
        """Parcourt tous les joueurs de la table, à partir du speaker."""
        speaker_id = self.speaker.id
        for player in self.players[speaker_id:] + self.players[:speaker_id]:
            yield player

    def __len__(self):
        return len(self.players) + len(self.wait_in) - len(self.wait_out)

    def next_player(self, player):
        return self.players[(player.id + 1) % self.nb_players]

    def print(self, *values, sep=" ", end="\n"):
        if self.verbose:
            print(*values, sep, end)

    def pause_game(self):
        while self.in_change:
            time.sleep(2)

    # ******************* PREPARATION DE LA PARTIE *********************
    def set_up_game(self):
        """gère le lancement de chaque nouvelle partie"""
        self.check_player_stack()
        self.check_len()
        self.protocole_deconnexion()
        if not self.end:
            self.initialisation_attributs()
            self.game()

    def protocole_deconnexion(self):
        """protocole deconnexion forcée client cf tournoi.changement_table"""
        self.in_game = False
        if self.redistribution:
            self.salon.redistribution(self)
        time.sleep(1)
        if not self.in_change:
            self.in_game = True
        else:
            self.pause_game()
        self.manage_file()

    def manage_file(self):
        """ gere les joueurs qui attendent d'entrer ou sortir de la table"""
        self.in_change = True
        changes = False
        while self.wait_in:
            ft.add_player(self, self.wait_in.pop(0))
            changes = True
        while self.wait_out:  # players disconnected
            ft.delete(self, self.wait_out.pop(0))
            changes = True
        if changes:
            ft.init_client_table(self)
        self.in_change = False

    def check_player_stack(self):
        """vérifie si un joueur n'est pas à stack==0"""
        for player in self.players:
            if player.stack < self.bb:
                ft.delete(self, player)
                fs.try_send(player, {"flag:":"disconect"})
                time.sleep(0.1)
                player.connexion.close()

    def check_len(self):
        """verifie si il reste des joueurs dans la table"""
        self.manage_file()
        if len(self) == 0:
            self.salon.del_table(self)
        elif len(self.players) == 1:
            print('len1')
            unique_joueur = self.players[0]
            salon = unique_joueur.salon
            if len(salon.tables) == 1:
                self.end = True
                print(unique_joueur.name, "a gagné")
            else:
                salon.gerer_joueur_seul(self, unique_joueur)
        self.manage_file()

    def initialisation_attributs(self):
        """initialise les attributs de la table pour commencer une nouvelle partie"""
        for player in self.players:
            player.hand = []
            player.is_all_in = player.is_folded = False
            player.final_hand = None
            player.on_going_bet = 0
        self.dealer = self.next_player(self.dealer)
        self.speaker = self.next_player(self.dealer)
        self.pots, self.cards, self.final_winners = map(list, ([] for _ in range(3)))
        self.deck.reinitialize()
        self.final_hand = False

    # ********************  LANCEMENT DE LA PARTIE  ***************
    def game(self):
        all_folded = False
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            round_ob()
            self.manage_pots()
            if self.folded_players() == self.nb_players - 1:
                all_folded = True
                break
        self.final_hand = True
        self.give_pots(all_folded)

    def pre_flop(self):
        print("Dealer", self.dealer.name)
        self.deal_and_blinds()
        self.players_speak(self.bb)

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.pop())
        sb_player = self.speaker
        sb_player.speaks(self.sb, blind=True)
        self.speaker = self.next_player(self.speaker)
        bb_player = self.speaker
        bb_player.speaks(self.bb, blind=True)
        self.speaker = self.next_player(self.speaker)
        fs.refresh_new_game(self, sb_player, bb_player)  # envoie aux clients les infos du tour cf fonction_serveur

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.pop() for _ in range(3)]
        self.print(" -".join([str(card) for card in self.cards]))
        fs.refresh_update(self)
        self.players_speak()

    def initialise_round(self):
        for player in self.players:
            player.on_going_bet = 0
        self.speaker = self.next_player(self.dealer)

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.pop()]
        self.print(" -".join([str(card) for card in self.cards]))
        fs.refresh_update(self)
        self.players_speak()

    def players_speak(self, mise: float = 0, raiser=None):
        for player in self:
            if self.active_players() == 1 and player.on_going_bet == mise:
                return
            if player == raiser or player.is_all_in or player.is_folded:
                continue
            # TODO: implémenter timer et renvoyer decision time dans player.speaks
            action, amount, decision_time = player.speaks(mise)
            self.history.append(
                (self.distance_to_dealer(player),
                 ["r", "c", "f"].index(action),
                 amount,
                 decision_time,
                 player.get_current_best_hand())
            )
            self.speaker = self.next_player(self.speaker)  # on passe mtn au prochain en cas de raise
            fs.refresh_update(self)  # envoie aux clients les nouvelles infos de la table cf fonction_serveur
            if action == 'r':
                return self.players_speak(amount, raiser=player)

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

    # FIN DE LA PARTIE
    def get_final_hands(self):
        """ Assigne à chaque joueur non couché sa main finale, c'est à dire sa meilleure combinaison de 5 cartes"""
        for player in self.players:
            if not player.is_folded:
                possible_hands = [Hand5(i) for i in combinations(self.cards + player.hand, 5)]
                player.final_hand = max(possible_hands)

    @staticmethod
    def get_winners(players):
        """Prend une liste de joueurs en entrée, renvoie les vainqueurs (meilleures mains finales)"""
        players_hands = [(player.final_hand, player) for player in players if not player.is_folded]
        winners = utils.maxes(players_hands, key=lambda players_hand: players_hand[0])  # max selon la main du joueur
        return [pot_winner[1] for pot_winner in winners]

    def give_pots(self, all_folded=False):
        """Répartit chaque pot à ses vainqueurs"""
        winner = None
        if all_folded:
            winner = [player for player in self.players if not player.is_folded][0]
            self.print(f"Everyone folded, {winner} wins {sum(v for v, _ in self.pots)}")
            self.final_winners = [winner]
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
            self.final_winners = pot_winners[:]
        fs.refresh_update(self)
        fs.refresh_end_game(self)
        time.sleep(5)

    def give_pot_total(self):
        pot_total = 0
        for pot in self.pots:
            pot_total += pot[0]
        return pot_total
