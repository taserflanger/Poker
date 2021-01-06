from itertools import combinations

from inputimeout import inputimeout, TimeoutOccurred
from time import time

from hand_5 import Hand_5


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
            try_send(self, "action".encode("utf-8"))
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
        print(f"{self.name} folds")
        return 'f', 0

    def print_action(self, player_action, bet, blind):
        txt = "not implemented error"
        if self.is_all_in:
            txt = f"is now all in and bets {bet}"
        elif blind:
            txt = f"puts a blind of {bet}"
        elif player_action == "c":
            txt = f"calls for {bet}" if bet > 0 else f"checks"
        elif player_action == "r":
            txt = f"raises for {bet}."
        elif player_action == "f":
            txt = f"folds"
        self.table.print(self.name, txt, f"     (new stack: {self.stack})")

    def get_current_best_hand(self):
        # ne fonctionne qu’à partir du flop
        if len(self.table.cards) == 0:
            return -1
        return Hand_5.types_ranking.index(max([Hand_5(i) for i in combinations(self.table.cards + self.hand, 5)]).type)
