import random
import numpy as np
from server.bot.monte_carlo.odds import give_odds
from server.bot.Bot import Bot
#from odds import give_odds



class BotMatheux(Bot):
    def __init__(self, bot_name, bot_stack):
        super().__init__(bot_name, bot_stack)
        self.coef_bluff = 1.5

    def softmax(self, x):
        return np.exp(x)/sum(np.exp(x))

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
            reference_ratio=1/num_opp
            action_proba = self.softmax([self.coef_bluff*exp_winnings/reference_ratio, 1])[0]
            x = random.random()
            if x < action_proba or amount_to_call<=5:
                player_action = "c"
                average_stack=sum([players.stack for players in self.table.players])/len(self.table.players)
                coef_richesse=self.stack/average_stack
                proba_raise=self.softmax([coef_richesse*self.coef_bluff*exp_winnings/reference_ratio, 1])[0]
                y=random.random()
                if y < proba_raise:
                    player_action=max(proba_raise*10*self.table.bb, amount_to_call)
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
        #self.print_action(player_action, bet, blind)
        return player_action, bet, 0

