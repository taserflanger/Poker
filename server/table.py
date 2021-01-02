# -*- coding: utf-8 -*-
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
        self.players = table_players
        self.nb_players = len(self.players)
        self.give_players_ids()
        if id_dealer == "random":
            self.dealer = self.players[random.randint(0, self.nb_players - 1)]
        else:
            self.dealer = self.players[id_dealer]
        self.speaker = self.next_player(self.dealer)
        self.sb, self.bb = small_blind, big_blind
        self.deck = Deck()
        self.cards, self.pots, self.final_winners, self.wait_in, self.wait_out=map(list, ([] for i in range(5)))
        self.final_hand, self.in_change, self.in_game, self.end, self.redistribution=map(bool, (False for i in range(5)))
        
    def __iter__(self):
        """Parcourt tous les joueurs de la table, à partir du speaker."""
        speaker_id = self.speaker.id
        for player in self.players[speaker_id:] + self.players[:speaker_id]:
            yield player

    def init_client_table(self):
        for joueur in self.players:
            f_s.try_send(joueur, {"flag":"init_table", "players_data":[{"name":gamer.name, "id":gamer.id, "stack": gamer.stack, "condition": False} for gamer in self.players]})
            

    def give_players_ids(self):
        i = 0
        for player in self.players:
            player.id = i
            i += 1

    def manage_file(self):
        """ gere les joueurs qui attendent d'entrer ou sortir de la table"""
        self.in_change=True
        changes=False
        while self.wait_in:
            self.add_player(self.wait_in.pop(0))
            changes=True
        while self.wait_out: #players disconnected
            #print(self.wait_out, self.wait_in)
            self.delete(self.wait_out.pop(0))
            changes=True
        if changes:
            self.init_client_table()
        self.in_change=False
        
    def set_up_game(self):
        self.check_player_stack()        
        self.check_len()
        self.protocole_deconnexion()
        if not self.end:
            self.initialisation_attributs()
            self.game()
    
    def protocole_deconnexion(self):
        """protocole deconnexion forcée client cf tournoi.changement_table"""
        self.in_game=False
        if self.redistribution==True:
            salon=self.players[0].salon # moche à changer
            salon.redistribution(self)  
        time.sleep(10)        
        if not self.in_change:
            self.in_game=True
        else:
            self.pause_game() 
        self.manage_file()
    
    def pause_game(self):
        while self.in_change: 
            time.sleep(2)
    
    def check_len(self):
        """verifie si il reste des joueurs dans la table"""
        self.manage_file() 
        if len(self.players) == 1:
            print('len1')
            unique_joueur=self.players[0]
            salon=unique_joueur.salon
            if len(salon.tables) == 1:
                self.end=True
                salon.vainqueur(unique_joueur)
            else:
                salon.gerer_joueur_seul(self, unique_joueur) 
        self.manage_file()
        
    def delete(self, player):
        print("ciao ", player.name)
        self.players.remove(player)
        self.nb_players-=1
        self.give_players_ids() 
        
    def add_player(self, player):
        print("hello", player.name, "has joined", self)
        self.players.append(player)
        player.id=self.nb_players
        self.nb_players+=1
        player.table=self
    
    def __len__(self):
        return len(self.players) + len(self.wait_in) - len(self.wait_out)

    def check_player_stack(self):
        """vérifie si un joueur n'est pas à stack==0"""
        for player in self.players:
            if player.stack < self.bb:
                self.delete(player)
                player.connexion.close()
                
    def next_player(self, player):
        return self.players[(player.id + 1) % self.nb_players]
        
    def game(self):
        all_folded=False
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            round_ob()
            self.manage_pots()
            if self.folded_players() == self.nb_players - 1:
                all_folded = True
                break
        self.final_hand=True
        self.give_pots(all_folded)
    
    def pre_flop(self):
        print("Dealer", self.dealer.name)
        self.deal_and_blinds()
        self.players_speak(self.bb)
    
    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            blind_amount = [self.sb, self.bb][i]
            self.speaker.speaks(blind_amount, blind=True)
            self.speaker = self.next_player(self.speaker)
        f_s.initialiser_actualisation(self, self.sb, self.bb)  # envoie aux clients les infos du tour cf fonction_serveur
    
    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for _ in range(3)]
        print([str(card) for card in self.cards])
        f_s.actualiser(self)
        self.players_speak()

    def initialise_round(self):
        for player in self.players:
            player.on_going_bet = 0
        self.speaker = self.next_player(self.dealer)

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        f_s.actualiser(self)
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
            self.final_winners=[winner]
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
        f_s.actualsation_finale(self)
    
    def give_pot_total(self):
        pot_total=0
        for pot in self.pots:
            pot_total+=pot[0]
        return pot_total

    def initialisation_attributs(self):
        for player in self.players:
            player.hand = []
            player.is_all_in = player.is_folded = False
            player.final_hand = None
            player.on_going_bet=0
        self.dealer = self.next_player(self.dealer)
        self.speaker = self.next_player(self.dealer)
        self.pots = []
        self.cards = []
        self.deck = Deck()
        self.final_winners= []
        self.final_hand=False
