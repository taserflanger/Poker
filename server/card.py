class Card:
    """
    Carte: représentée par un dictionnaire
    """
    def __init__(self, card_value: int, card_suit: int):
        """
        constructeur d’une carte
        :param card_value: hauteur de la carte (as = 14)
        :param card_suit: coulour de la carte (trèfle, carreau, coeur, pique)
        """
        self.suit = card_suit
        self.value = card_value
        self.img = str(self.value) + '_' + str(self.suit) + '.png'

    dic_values = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'Jack', 12: 'Queen',
                  13: 'King', 14: 'Ace'}
    dic_suits = {0: 'clubs', 1: 'diamonds', 2: 'hearts', 3: 'spades'}

    def __str__(self):
        return Card.dic_values[self.value] + ' of ' + Card.dic_suits[self.suit]

    def __repr__(self):
        return Card.dic_values[self.value] + ' of ' + Card.dic_suits[self.suit]
