import random
from typing import List

from .card import Card


class Deck(List):
    """
    Paquet de cartes. C’est une liste de taille et éléments fixés, qui implément shuffle.
    """

    def __init__(self):
        """initialise un paquet de cartes mélangé aléatoirement"""
        super().__init__()
        self.reinitialize()

    def reinitialize(self):
        for value in list(range(2, 15)):
            for suit in list(range(4)):
                self.append(Card(card_value=value, card_suit=suit))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self)
  
    def remove(self, card):
        card_value=card.value
        card_suit=card.suit
        for card in self:
            if card_value==card.value and card_suit==card.suit:
                super(Deck, self).remove(card)
                return

