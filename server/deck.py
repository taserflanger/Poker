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
        """Enlève une carte à la fin du paquet et la renvoie"""

        last_card_ind = len(self.cards) - 1
        card = self.cards[last_card_ind]
        self.cards = self.cards[:-1]

        return card
print("test_linode_pull")