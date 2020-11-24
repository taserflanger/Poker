from inputimeout import inputimeout, TimeoutOccurred
from time import time


class Player:

    def __init__(self, player_name, player_stack):
        self.name = player_name
        self.stack = player_stack
        self.id = None  # position sur la table
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

        lastimeout = 120
        if not blind:  # si c'est une blinde, on ne demande pas l'avis du joueur
            while player_action not in ['f', 'c', 'r'] or (player_action == 'r' and bet >= self.stack):
                a = time()
                try:
                    player_action = inputimeout(
                        prompt=f"{self.name} : {c} (c), raise (r), fold (f) ?        "
                               f"({round(lastimeout)}s left --- stack: {self.stack})\n",
                        timeout=lastimeout)
                except TimeoutOccurred:
                    print("too slow to make a decision")
                    player_action = "f"
                lastimeout -= time() - a
                if player_action == 'r' and bet >= self.stack:
                    print("not enough money to reraise")
        decision_time = 120 - lastimeout
        if player_action == 'c' or blind:
            bet = self.calls(bet)
        elif player_action == 'r':
            bet = self.raises(bet)
        elif player_action == 'f':
            self.is_folded = True
            bet = 0
        self.stack -= bet
        self.on_going_bet += bet
        if self.stack == 0:
            self.is_all_in = True
        self.print_action(player_action, bet, blind)
        return player_action, bet, decision_time

    def calls(self, bet):
        if bet > self.stack:
            bet = self.stack
        return bet

    def raises(self, bet):
        raise_val = float("inf")
        while raise_val > self.stack - bet:
            raise_val = int(input(f"Raise? (max-raise: {self.stack - bet})  "))
        return raise_val + bet

    def print_action(self, player_action, bet, blind):
        txt = "not implemented error"
        if self.is_all_in:
            txt = f"{self.name} is now all in and bets {bet} "
        elif blind:
            txt = f"{self.name} puts a blind of {bet}"
        elif player_action == "c":
            txt = f"calls for {bet}" if bet > 0 else f"checks"
        elif player_action == "r":
            txt = f"raises for {bet}."
        elif player_action == "f":
            txt = f"folds"
        print(self.name, txt)
