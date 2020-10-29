class Player:

    def __init__(self, player_name, player_stack, player_id):
        self.name = player_name
        self.stack = player_stack
        self.id = player_id  # position sur la table
        self.hand = []
        self.on_going_bet = 0
        self.score=0 #utile pour la fonction determiner gagnant

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
                print("all-in!")
                diff = self.stack
            bet = diff
        elif player_action == 'r':
            raise_val = float("inf")
            while raise_val > self.stack:
                raise_val = int(input('Raise = '))
            bet = raise_val + diff
        self.stack -= bet
        self.on_going_bet += bet
        print(f"{self.name} " + {'c': 'calls', 'r': 'raises', 'f': 'folds'}[player_action] + f" and bets {bet}.")
        return player_action, raise_val
