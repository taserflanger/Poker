import random
from math import exp

from server.bot.monte_carlo.odds import give_odds
from server.bot.Bot import Bot
#from odds import give_odds



class BotMatheux(Bot):
    def __init__(self, bot_name, bot_stack):
        super().__init__(bot_name, bot_stack)
        self.coef_bluff = 1

    def p(self, x):
        return 1 / (1 + exp(-self.coef_bluff * x))

    # + coef de bluff est bas + le bot bluff, il évolue entre 0 et +infini
    def speaks(self, amount_to_call, blind=False):
        """Ce bot fait uniquement en fonction des stats associées à ses cartes"""
        player_action = ''
        bet = amount_to_call - self.on_going_bet  # on initialise à la valeur du call
        board = self.table.cards
        num_opp = 0
        for player in self.table.players:
            if not player.is_folded:
                num_opp += 1
        if not blind:
            exp_winnings = give_odds(self.hand, board, num_opp)[1]
            proba = self.p(exp_winnings)
            x = random.random()
            if x < proba:
                player_action = "c"
                # ask if raise
            else:
                player_action = "f"
            if bet == 0:
                player_action = "c"
        if player_action == 'c' or blind:
            bet = self.calls(bet)
        elif player_action == 'f':
            return self.folds()
        else:  # si non (f) et non (c) c'est que le joueur raise
            bet = int(player_action)
            player_action = "r"
        self.stack -= bet
        self.on_going_bet += bet
        if self.stack == 0:
            self.is_all_in = True
        self.print_action(player_action, bet, blind)
        return player_action, bet, 0


