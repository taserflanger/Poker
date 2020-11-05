class Player:

    def __init__(self, player_name, player_stack, player_id):
        self.name = player_name
        self.stack = player_stack
        self.id = player_id  # position sur la table
        self.hand = []
        self.on_going_bet = 0
        self.score = 0 ### ANDRES ### #utile pour la fonction determiner gagnant
        self.is_all_in = self.is_folded = False

    def put_on_going_bet(self, amount):
        self.stack -= amount
        self.on_going_bet += amount

    def speaks(self, amount_to_call):
        player_action = ''
        bet = amount_to_call - self.on_going_bet  # on initialise à la valeur du call
        c = "call"
        if bet == 0:
            c = "check"
        while player_action not in ['f', 'c', 'r']:
            player_action = input(f"{self.name}, {amount_to_call} : {c} (c), raise (r), fold (f) ?\n")
        if player_action == 'c':
            bet = self.calls(bet)
        elif player_action == 'r':
            bet = self.raises(bet)
        elif player_action == 'f':
            self.is_folded = True
        self.stack -= bet
        self.on_going_bet += bet
        if self.stack == 0:
            self.is_all_in = True
            print(f"{self.name} is now all in with {bet} !")
        else:
            print(f"{self.name} " + {'c': 'calls', 'r': 'raises', 'f': 'folds'}[player_action] + f" and bets {bet}.")
        return player_action, bet

    def calls(self, bet):
        if bet > self.stack:
            bet = self.stack
        return bet

    def raises(self, bet):
        raise_val = float("inf")
        while raise_val > self.stack:
            raise_val = int(input(f"Raise? (current stack: {self.stack})  "))
        return raise_val + bet
