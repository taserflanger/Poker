from fonctions_serveur import remaniement
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
        self.deconnecte=False
        self.table=None
        self.tournoi=None

    def speaks(self, amount_to_call, blind=False):
        player_action = ''
        bet = amount_to_call - self.on_going_bet  # on initialise à la valeur du call
        c = "call"
        if bet == 0:
            c = "check"
        if not blind:  # si c'est une blinde, on ne demande pas l'avis du joueur       
            self.connexion.send("action joueur".encode("utf-8"))
            time.sleep(2)
            try:
                player_action = self.connexion.recv(1024).decode("utf-8")
                self.deconnecte=False
            except: #si le joueur ne repond pas 2 fois de suite alors il est deconnecté
                player_action='f'
                print(self.name, " n'a pas repondu")
                if self.deconnecte:
                    remaniement(self) #supprimer joueur et  créer une nouvelle table
                    pass
                else:
                    self.deconnecte=True

        if player_action == 'c' or blind:
            bet = self.calls(bet)
        elif player_action == 'f':
            return self.folds()
        else:                    # si non (f) et non (c) c'est que le joueur raise
            bet = int(player_action)
        time.sleep(0.05)
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
        if self.is_all_in:
            print(f"{self.name} is now all in and bets {bet} ")
        elif blind:
            print(f"{self.name} bets {bet}")
        else:
            print({'c': 'calls', 'r': 'raises'}[player_action] + f" and bets {bet}.")
