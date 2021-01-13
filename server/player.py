from itertools import combinations
from time import time

from typing import Tuple

from .hand5 import Hand5
from server.server_utils import try_send, try_recv
import json
import time


class Player:
    """
    Classe de base pour tout type de joueur. Un joueur s’interface avec une table à travers
    Player.speaks. Un Player est par défaut considéré comme contrôlé par un client du jeu,
    et on attend de lui qu’il réponde aux requêtes du serveur.
    Cependant, des classes de bots peuvent override l’interface table/joueur, ce qui permet de laisser
    la décision d’une action au serveur lui-même plutôt qu’à un client. Cela évite de devoir saturer
    les communications par les bots, notamment lorsqu’il y en a beaucoup qui jouent
    """

    def __init__(self, player_name, player_stack):

        self.name = player_name
        self.stack = player_stack
        self.id = None  # position sur la table
        self.hand = []
        self.on_going_bet = 0
        self.final_hand = None
        self.connexion = None
        self.infos_connexion = None
        self.ready = False
        self.disco = False  # disconnected
        self.is_all_in = self.is_folded = False
        self.table = None
        self.salon = None
        self.bot = False

    def speaks(self, amount_to_call: float, blind: bool = False) -> Tuple[str, float, int]:
        """
        renvoie player_action: f pour fold, r pour raise, c pour check/call
        Interface entre le joueur et la table. Peut être override pour les comportements particuliers
        :param amount_to_call: minimum pour suivre
        :param blind: si c’est une blinde, on ne demande pas l’avis du joueur
        :return: player_action, bet, decision_time
        """
        player_action = ''
        bet: float = amount_to_call - self.on_going_bet  # on initialise à la valeur du call
        if not blind:  # si c'est une blinde, on ne demande pas l'avis du joueur
            time.sleep(0.3)       
            try_send(self, {"flag": "action", "amount_to_call": amount_to_call})
            time.sleep(0.3)
            player_message = try_recv(self) if not self.disco else "f"
            if not player_message == "f":
                data: dict = json.loads(player_message)
                flag = data["flag"]
                while flag != "action" and data != "f":
                    player_message = try_recv(self) if not self.disco else "f"
                    if player_message!="f":
                        flag = json.loads(player_message)["flag"]
                player_action = data["action"]
            else:
                player_action = "f"
        if player_action == 'c' or blind:
            bet = self.calls(bet)
        elif player_action == 'f':
            return self.folds()
        else:  # si non (f) et non (c) c'est que le joueur raise
            bet = int(player_action) - self.on_going_bet
            player_action = "r"
        time.sleep(0.3)
        self.stack -= bet
        self.on_going_bet += bet
        if self.stack == 0:
            self.is_all_in = True
        self.print_action(player_action, bet, blind)
        return player_action, self.on_going_bet, 0

    def calls(self, bet: float) -> float:
        if bet > self.stack:
            bet = self.stack
        return bet

    def folds(self):
        self.is_folded = True
        #print(self.name, "folds")
        return 'f', 0, 0

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
        return Hand5.types_ranking.index(max([Hand5(i) for i in combinations(self.table.cards + self.hand, 5)]).type)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
