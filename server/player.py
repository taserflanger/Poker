# -*- coding: utf-8 -*-
from fonctions_serveur import try_send, try_recv
import json
import time
class Player:

    def __init__(self, player_name, player_stack):
        self.name = player_name
        self.stack = player_stack
        self.id = None  # position sur la table
        self.hand = []
        self.on_going_bet = 0
        self.is_all_in = self.is_folded = False
        self.final_hand = None
        self.connexion=None
        self.infos_connexion= None
        self.ready=False
        self.disco=False #disconnected
        self.table=None
        self.salon=None

    def speaks(self, amount_to_call, blind=False):
        player_action = ''
        bet = amount_to_call - self.on_going_bet  # on initialise à la valeur du call
        if not blind:  # si c'est une blinde, on ne demande pas l'avis du joueur       
            try_send(self, {"flag": "action"})
            time.sleep(0.3)
            player_action = try_recv(self) if not self.disco else "f"
        if player_action == 'c' or blind:
            bet = self.calls(bet)
        elif player_action == 'f':
            return self.folds()
        else:                    # si non (f) et non (c) c'est que le joueur raise
            bet = int(player_action)
            player_action="r"
        time.sleep(0.3)
        self.stack -= bet
        self.on_going_bet += bet
        if self.stack == 0:
            self.is_all_in = True
        self.print_action(player_action, bet, blind)
        return player_action, bet

    def calls(self, bet):
        if bet > self.stack:
            bet = self.stack
        return bet


    def folds(self):
        self.is_folded = True
        print(self.name, "folds")
        return 'f', 0

    def print_action(self, player_action, bet, blind):
        if self.is_all_in:
            print(self.name, "is now all in and bets", bet)
        elif blind:
            print(self.name, "bets", bet)
        else:
            print({'c': 'calls', 'r': 'raises'}[player_action] + " and bets", bet)
