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

        return self.cards.pop()

    def __len__(self):
        return len(self.cards)


    def remove(self, card):
        for deck_card in self.cards:
            if card.value==deck_card.value and card.suit == deck_card.suit:
                self.cards.remove(deck_card)



