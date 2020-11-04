"""
ATTENTION : l'opérateur '==' ne correspond pas à l'égalité exacte de la main (d'ailleurs impossible), mais à l'égalité
de la valeur de la main
VOC:

type (str) = le type de main, en prenant tout en compte
combi (str) = le type de main en fonction des combinaisons, sans compter les couleurs et les suites
top_comb (int entre 1 et 4) = la meilleure combinaison de cartes dans la main
top_comb_values (list) = les valeurs des cartes qui forment la top_comb
low_comb_values (list) = le reste des cartes (elles forment des hauteurs sauf dans le cas du full)

"""
from deck import Deck
from itertools import combinations
import time
import random_functions as r_f

class Hand_5:
    """Toute fonction commençant par c_ signifie 'compare'"""

    def __init__(self, cards):
        self.cards = sorted(cards, key= lambda card: card.value, reverse=True)  # trié par ordre décroissant de valeur
        self.suits = [card.suit for card in self.cards]
        self.values = [card.value for card in self.cards]
        self.type, self.top_comb_values, self.low_comb_values = self.get_type()
        # Dans le cas d'une suite, couleur, ou hauteur,self.low_comb_values = [

    types_ranking = [False, 'high', 'pair', 'two_pair', 'three', 'straight', 'flush', 'full', 'four', 'straight_flush']
    # on met le False en première position pour la méthode get_type()


    def get_type(self):
        """Renvoie le type de main """
        combi, top_comb_values, low_comb_values = self.get_combi()
        attributes = (self.is_flush(), self.is_straight(), combi)
        return max(attributes, key=lambda attr: Hand_5.types_ranking.index(attr)), top_comb_values, low_comb_values

    def is_flush(self):
        """Renvoie 'flush' si la main est une flush, False sinon"""
        if self.suits[0] * 5 == self.suits:
            return 'flush'
        else:
            return False

    def is_straight(self):
        """Renvoie 'straight' si la main est une suite, False sinon"""
        top_value = self.values[0]  # puisque cartes ordonnées
        if self.values == [i for i in range(top_value, top_value - 5, -1)]:
            return 'straight'
        else:
            return False

    def get_combi(self):
        """Renvoie le type de la main, concernant les combinaisons de cartes (paires, carrés, etc), sans considération
        des suites ou des couleurs; ainsi que les cartes concernées par ce type
        ex: renvoie ('brelan', 3) ou ('two_pair', [2, 5]), ou ('full', [3, 4]) pour un full des 3 par les 4"""
        hand_dict = {value : self.values.count(value) for value in set(self.values)}
        top_comb = max(hand_dict.values())  # le nombre maximal de cartes identiques (1, 2, 3 ou 4)
        top_comb_values = [value for value in hand_dict.keys() if hand_dict[value] == top_comb]
        low_comb_values = [value for value in hand_dict.keys() if value not in top_comb_values]

        if top_comb == 3 and 2 in hand_dict.values():  # pour le full
            combi = 'full'
        elif top_comb == 2 and len(top_comb_values) == 2:
            combi = 'two_pair'
        else:
            combi = {1: 'high', 2: 'pair', 3: 'three', 4: 'four'}[top_comb]
        return combi, top_comb_values, low_comb_values

    def c_same_type(hand1, hand2):
        """Renvoie un tuple (a, b) :    a = True si hand1 > hand2, False sinon
                                        b = True si hand1 == hand2, False sinon
        On peut ainsi utiliser cette fonction pour l'opérateur d'inégalité stricte, et celui de l'égalité"""

        for i in range(len(hand1.top_comb_values)):
            if hand1.top_comb_values[i] != hand2.top_comb_values[i]:
                return hand1.top_comb_values > hand2.top_comb_values, False
        for i in range(len(hand1.low_comb_values)):
            if hand1.low_comb_values[i] != hand2.low_comb_values[i]:
                return hand1.low_comb_values > hand2.low_comb_values, False
        return False, True  # dans le cas où on n'a pas réussi à départager les deux mains

    def __gt__(self, other_hand):
        if other_hand is None:  # utile dans la méthode Table.get_winner()
            return True
        type_ids = (Hand_5.types_ranking.index(self.type), Hand_5.types_ranking.index(other_hand.type))
        if type_ids[0] > type_ids[1]:
            return True
        elif type_ids[0] == type_ids[1]:
            return Hand_5.c_same_type(self, other_hand)[0]
        else:
            return False

    def __eq__(self, other_hand):
        type_ids = (Hand_5.types_ranking.index(self.type), Hand_5.types_ranking.index(other_hand.type))
        if type_ids[0] == type_ids[1]:
            return Hand_5.c_same_type(self, other_hand)[1]
        else:
            return False

    def __ge__(self, other_hand):
        return self > other_hand or self == other_hand

    def __lt__(self, other_hand):
        return other_hand > self

    def __le__(self, other_hand):
        return self < other_hand or self == other_hand

def test_class(nb_players=6):
    deck = Deck()
    table_cards = [deck.deal() for _ in range(5)]
    players_cards = [[deck.deal() for _ in range(2)] for _ in range(nb_players)]
    players_fh = [None] * nb_players
    print("table cards: ", [str(card) for card in table_cards])
    t1 = time.time()
    for i in range(nb_players):
        print(f"player {i} cards: ", [str(card) for card in players_cards[i]])
        possible_hands = [Hand_5(i) for i in combinations(table_cards + players_cards[i], 5)]
        best_hand = max(possible_hands)
        players_fh[i] = best_hand
    ranked_hands = r_f.rank_dict(players_fh)
    best_hand = max(players_fh)
    t2 = time.time()
    for i in range(nb_players):
        print(f"player {i} : rank {ranked_hands[i]}")
    print("Meilleure main : player ", players_fh.index(best_hand), [str(card) for card in best_hand.cards])
    print(f"Temps d'exécution : {round((t2-t1)*1000, 5)} ms")

if __name__ == '__main__':
    test_class()


