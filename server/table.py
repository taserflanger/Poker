from deck import Deck


import random
from deck import Deck
from hand_5 import Hand_5
from itertools import combinations
import random_functions as r_f
import fonctions_serveur as f_s
import time



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
        self.final_hand= False
        self.final_winners= []
        self.in_game=False
        self.in_change=False

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
        self.in_game=False   #protocole deconnexion forcée client cf tournoi.changement_table
        time.sleep(10)        
        if not self.in_change:
            self.in_game=True
        else:
            self.end_game()

        for player in self.players:
            player.hand = []
            player.is_all_in = player.is_folded = False
            player.final_hand = None
            player.on_going_bet=0
        self.dealer = self.next_player(self.dealer)
        self.speaker = self.next_player(self.speaker)
        self.pots = []
        self.cards = []
        self.deck = Deck()
        self.final_winners= []
        self.final_hand=False
        
    def end_game(self):
        for player in self.players:
            player.connexion.send("Un joueur s'est déconnecté sur une table, attendez un instant ".encode())
        while self.in_change: #attente de suppression de la table, ou d'ajout d'un joueur
            time.sleep(10)
        
    def check_player_stack(self):
        for player in self.players:
            if player.stack < self.bb:
                self.players.remove(player)
                player.tournoi.supprimer_joueur(player) 
        
    def next_player(self, player):
        return self.players[(player.id + 1) % self.nb_players]

    def initialise_round(self):
        for player in self.players:
            player.on_going_bet = 0
        self.speaker = self.next_player(self.dealer)
        
    def game(self):
        all_folded = False
        self.set_up_game()
        self.check_player_stack()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            round_ob()
            self.manage_pots()
            if self.folded_players() == self.nb_players - 1:
                all_folded = True
                break
        self.final_hand=True
        self.give_pots(all_folded)

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            blind_amount = [self.sb, self.bb][i]
            self.speaker.speaks(blind_amount, blind=True)
            self.speaker = self.next_player(self.speaker)
        f_s.initialiser_actualisation(self, self.sb, self.bb)  # envoie aux clients les infos du tour cf fonction_serveur
        time.sleep(1)

    def pre_flop(self):
        print(f'Dealer : {self.dealer.name}')
        self.deal_and_blinds()
        self.players_speak(self.bb)

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for _ in range(3)]
        print([str(card) for card in self.cards])
        f_s.actualiser(self)
        time.sleep(1)
        self.players_speak()

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        self.players_speak()

    def players_speak(self, mise=0, raiser=None):
        for player in self:
            if self.active_players() == 1:
                return
            if player == raiser or player.is_all_in or player.is_folded:
                continue
            action, amount = player.speaks(mise)
            self.speaker = self.next_player(self.speaker)  # on passe mtn au prochain en cas de raise
            f_s.actualiser(self)  # envoie aux clients les nouvelles infos de la table cf fonction_serveur 
            time.sleep(0.3)
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

    def get_final_hands(self):
        """ Assigne à chaque joueur non couché sa main finale, c'est à dire sa meilleure combinaison de 5 cartes"""
        for player in self.players:
            if not player.is_folded:
                possible_hands = [Hand_5(i) for i in combinations(self.cards + player.hand, 5)]
                player.final_hand = max(possible_hands)

    def get_winners(self, players):
        """Prend une liste de joueurs en entrée, renvoie les vainqueurs (meilleures mains finales)"""
        players_hands = [(player.final_hand, player) for player in players if not player.is_folded]
        winners = r_f.maxes(players_hands, key=lambda players_hand: players_hand[0])  # max selon la main du joueur
        return [pot_winner[1] for pot_winner in winners]


    def give_pots(self, all_folded=False):
        """Répartit chaque pot à ses vainqueurs"""
        if all_folded:
            winner = [player for player in self.players if not player.is_folded][0]
            self.final_winners=winner
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
                player.stack += value_for_player
                pot_value -= value_for_player
                n -= 1
            self.final_winners= pot_winners[:]
        f_s.actualiser(self)
        time.sleep(0.3)

