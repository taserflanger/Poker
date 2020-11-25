from itertools import combinations

from inputimeout import inputimeout, TimeoutOccurred
from time import time

from hand_5 import Hand_5


class Player:

    def __init__(self, player_name, player_stack):
        self.name = player_name
        self.stack = player_stack
        self.id = None  # position sur la table
        self.table = None #table attribuée (None par défaut)
        self.hand = []
        self.on_going_bet = 0
        self.is_all_in = self.is_folded = False
        self.final_hand = None

    def speaks(self, amount_to_call, blind=False):
        player_action = ''
        bet = amount_to_call - self.on_going_bet  # on initialise à la valeur du call
        c = "check"
        if bet > 0:
            c = f"{bet} to call {amount_to_call}"
        a = time()
        player_action = self.ask_action(bet, blind, c, player_action, 120)
        decision_time = time() - a
        # on calcule le temps de décision car ask_action est implémenté sans timer pour les bots
        if player_action == 'c' or blind:
            bet = self.calls(bet)
        if player_action == 'r':
            a = time()
            bet, player_action = self.ask_amount(bet, 120 - decision_time)
            decision_time += time() - a
        if player_action == 'f':
            self.is_folded = True
            bet = 0
        self.finalize_action(bet, blind, player_action)
        return player_action, bet, decision_time

    def finalize_action(self, bet, blind, player_action):
        self.stack -= bet
        self.on_going_bet += bet
        if self.stack == 0:
            self.is_all_in = True
        self.print_action(player_action, bet, blind)

    def ask_action(self, bet, blind, c, player_action, max_time):
        lastimeout = max_time
        if not blind:  # si c'est une blinde, on ne demande pas l'avis du joueur
            while player_action not in ['f', 'c', 'r'] or (player_action == 'r' and bet >= self.stack):
                a = time()
                try:
                    player_action = inputimeout(
                        prompt=f"{self.name} : {c} (c), raise (r), fold (f) ?        "
                               f"({round(lastimeout)}s left --- stack: {self.stack})\n",
                        timeout=lastimeout)
                except TimeoutOccurred:
                    #print("too slow to make a decision")
                    player_action = "f"
                lastimeout -= time() - a
                if player_action == 'r' and bet >= self.stack:
                    #print("not enough money to reraise")
                    pass
        return player_action

    def calls(self, bet):
        if bet > self.stack:
            bet = self.stack
        return bet

    def ask_amount(self, bet, remaining_time):
        raise_val = float("inf")
        while raise_val > self.stack - bet:
            try:
                raise_val = int(inputimeout(f"Raise? (max-raise: {self.stack - bet})  "))
            except TimeoutOccurred:
                return 0, "f"
        return raise_val + bet, "r"

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
        #print(self.name, txt, f"     (new stack: {self.stack})")

    def get_current_best_hand(self):
        # ne fonctionne qu’à partir du flop
        if len(self.table.cards) == 0:
            return -1
        return Hand_5.types_ranking.index(max([Hand_5(i) for i in combinations(self.table.cards + self.hand, 5)]).type)
