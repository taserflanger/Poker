# -*- coding: utf-8 -*-
import random
from card import Card


class Deck:

    def __init__(self, standard=True):

        self.cards = []
        for value in list(range(2, 15)):
            for suit in list(range(4)):
                self.cards.append(Card(card_value=value, card_suit=suit))

        random.shuffle(self.cards)

    def deal(self):
        """Enleve une carte a la fin du paquet et la renvoie"""

        last_card_ind = len(self.cards) - 1
        card = self.cards[last_card_ind]
        self.cards = self.cards[:-1]

        return card   #peut etre on peut remplacer par self.cards.pop(-1) ?

    def remove(self, card):
        for deck_card in self.cards:
            if card.value==deck_card.value and card.suit==deck_card.suit:
                self.cards.remove(deck_card)



