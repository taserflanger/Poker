from deck import Deck


import random
from deck import Deck
from hand_5 import Hand_5
from itertools import combinations
import random_functions as r_f

#TODO: -rank_hands ne fonctionne pas si plus d'un joueur s'est fold, car comparaison impossible entre deux None
#      - modifier player et main pour ne pas avoir à créer les joueurs avec un id : l'id est propre à la table,
#       et non au joueur en lui-même.




class Table:

    def __init__(self, table_players, small_blind, big_blind, id_dealer="random"):
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

    def __iter__(self):
        """Parcourt tous les joueurs de la table, à partir du speaker."""
        speaker_id = self.speaker.id
        for player in self.players[speaker_id:] + self.players[:speaker_id]:
            yield player

    def give_players_ids(self):
        i = 0
        for player in self.players:
            player.id = i
            i += 1

    def set_up_game(self):
        for player in self.players:
            player.hand = []
            player.is_all_in = player.is_folded =  False
            player.final_hand = None
        self.dealer = self.next_player(self.dealer)
        self.speaker = self.next_player(self.speaker)
        self.pots = []
        self.cards = []
        self.deck = Deck()

    def next_player(self, player):
        return self.players[(player.id + 1) % self.nb_players]

    def initialise_round(self):
        for player in self.players:
            player.on_going_bet = 0
        self.speaker = self.next_player(self.dealer)

    def game(self):
        self.set_up_game()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            one_player_active = round_ob()
            self.manage_pots()
            if one_player_active and self.folded_players() == self.nb_players - 1:
                break
        self.give_pots()

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            blind_amount = [self.sb, self.bb][i]
            self.speaker.speaks(blind_amount, blind=True)
            self.speaker = self.next_player(self.speaker)

    def pre_flop(self):
        print(f'Dealer : {self.dealer.name}')
        self.deal_and_blinds()
        self.players_speak(self.bb)

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for _ in range(3)]
        print([str(card) for card in self.cards])
        self.players_speak()

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        self.players_speak()

    def players_speak(self, mise=0, raiser=None):
        for player in self:
            if self.active_players() == 1:
                return True
            if player == raiser or player.is_all_in or player.is_folded:
                continue
            action, amount = player.speaks(mise)
            self.speaker = self.next_player(self.speaker)  # on passe mtn au prochain en cas de raise
            if action == 'r':
                return self.players_speak(amount, raiser=player)

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

    def rank_hands(self):
        """ Renvoie un dictionnaire avec, pour chaque indice de joueur, le rang de sa main parmi tous les joueurs.
        On fait ça pour gérer les cas d'égalité"""
        players_hands = [None] * self.nb_players
        remaining_players = self.pots[0][1]  # indices des joueurs participant à au moins 1 pot
        for player_id in range(self.nb_players):
            player = self.players[player_id]
            if player_id in remaining_players:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.hand, 5)]
                players_hands[player_id] = player.final_hand = max(possible_hands)

        ranked_hands = r_f.rank_dict(players_hands)
        return ranked_hands


    def give_pots(self):
        """Répartit chaque pot à ses vainqueurs"""
        #TODO : pour l'instant, je pense qu'on peut donner de l'argent à quelqu'un qui est couché, ce qui n'est pas
        # normal
        ranked_hands = self.rank_hands()  # un dictionnaire avec pour chaque player_id, son rang sur la table
        for pot in self.pots:
            pot_players = pot[1]  # les joueurs qui participent à ce pot
            pot_winners = r_f.maxes(pot_players, key=lambda p_id: ranked_hands[p_id])
            for player_id in pot_winners:
                n = len(pot_winners)
                self.players[player_id].stack += round(pot[0] // n)  ### voir plus tard le cas où ce n'est pas un entier
