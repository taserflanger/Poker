from abc import abstractmethod
from random import randint, choice
from typing import Tuple

from server import Player


class Bot(Player):
    def __init__(self, player_name: str, player_stack: int):
        super().__init__(player_name, player_stack)
        self.bot = True

    @abstractmethod
    def speaks(self, amount_to_call: float, blind: bool = False) -> Tuple[str, float, int]:
        """Ce bots fait du random"""
        bet = randint(1, self.stack - amount_to_call)
        action = choice(["f", "c", "r"])
        return action, bet, 0
