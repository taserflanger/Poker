class Player:

    def __init__(self, player_name, player_stack, player_id):
        self.name = player_name
        self.stack = player_stack
        self.id = player_id  # position sur la table
        self.hand = []
        self.on_going_bet = 0
        self.score = 0  ### ANDRES ### #utile pour la fonction determiner gagnant
        self.is_all_in = False
        self.folded = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def put_on_going_bet(self, amount):
        self.stack -= amount
        self.on_going_bet += amount

    def speaks(self, amount_to_call):
        player_action = ''
        diff = amount_to_call - self.on_going_bet
        c = "call"
        bet = 0
        raise_val = 0
        if diff == 0:
            c = "check"
        while player_action not in ['f', 'c', 'r']:
            player_action = input(f"{self.name}, {amount_to_call} : {c} (c), raise (r), fold (f) ?\n")
        if player_action == 'c':
            # TODO: - détecter lorsqu'un raise/call est un all-in.
            #  Faire en sorte qu'on ne peut pas gagner trop lorsqu'on
            #  se met all-in avec pas grand chose (selon les variantes c'est plus ou moins strict je crois)
            if diff > self.stack:
                diff = self.stack
            bet = diff
        elif player_action == 'r':
            raise_val = float("inf")
            while raise_val+diff > self.stack:
                raise_val = int(input(f"Raise? (current stack: {self.stack}, max reraise: {self.stack - diff})  "))
            bet = raise_val + diff
        self.put_on_going_bet(bet)
        if self.stack == 0:
            self.is_all_in = True
            print(f"{self.name} is now all in!")
        else:
            print(f"{self.name} " + {'c': 'calls', 'r': 'raises', 'f': 'folds'}[player_action] + f" and bets {bet}.")
        return player_action, raise_val
