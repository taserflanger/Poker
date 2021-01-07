from random import randint, choice

from ..player import Player


class Bot(Player):
    def __init__(self, player_name: str, player_stack: int):
        super().__init__(player_name, player_stack)

    def speaks(self, amount_to_call: float, blind: bool = False) -> tuple[str, float, int]:
        """Ce bot fait du random"""
        bet = randint(1, self.stack - amount_to_call)
        action = choice("f", "c", "r")
        return action, bet, 0
