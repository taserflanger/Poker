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
            """
            balise1={"jouer": True}
            balise1_encodé=json.dumps(balise1)
            self.connexion.send(balise1_encodé.encode())
            """
            self.connexion.send("jouer".encode())
            time.sleep(2)
            while player_action not in ['f', 'c', 'r']:
                self.connexion.send(str(f"{self.name}, {amount_to_call} : {c} (c), raise (r), fold (f) ?\n").encode())
                try:
                    player_action = self.connexion.recv(1024).decode()
                    print("p_a", player_action)
                    self.deconnecte=False
                except: #si le joueur ne repond pas 2 fois de suite alors il est deconnecté
                    player_action='f'
                    print("error")
                    if self.deconnecte:
                        remaniement(self) #supprimer joueur et  créer une nouvelle table
                        pass
                    else:
                        self.deconnecte=True

        if player_action == 'c' or blind:
            bet = self.calls(bet)
        elif player_action == 'r':
            bet = self.raises(bet)
        elif player_action == 'f':
            return self.folds()
        time.sleep(0.05)
        balise2="fin action"
        self.connexion.send(balise2.encode())
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

    def raises(self, bet):
        balise3="raise"
        self.connexion.send(balise3.encode())
        infos=str("current stack: " + str(self.stack) + "\n Raise how much?")  
        self.connexion.send(infos.encode())
        raise_val = float("inf")
        while raise_val > self.stack: #ajouter un try
            try: 
                raise_val = int(self.connexion.recv(1024).decode())
                if raise_val > self.stack:
                    self.connexion.send("erreur".encode())
            except:
                self.deconnecte=True
                self.player_action="f"
                self.folds()
        balise4="fin raise"
        self.connexion.send(balise4.encode())
        return raise_val + bet

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
