from random import shuffle

class Deck:
    def __init__(self):
        self.cards = [f"{str(name)}{color}"
                      for color in ("c", "t", "p", "c")
                      for name in range(1, 13)]

    def __getitem__(self, item):
        return self.cards[item]

    def pop(self):
        return self.cards.pop()

    def shuffle(self):
        shuffle(self.cards)
