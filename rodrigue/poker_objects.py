"""
L'itérateur de la classe table permet de parcourir les joueurs restant dans la main, à partir de celui qui doit parler
en premier.
Pour jouer une main:

TODO:   - s'occuper de la fonctionnalité fold
        - s'occuper du cas de figure ou tout le monde sauf 1 s'est couché
        - retranscrire dans un modèle client/serveur, où le client n'a accès qu'aux informations qui le concernent
"""
import random
from math import inf
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

class Player:

    def __init__(self, player_name, player_stack, player_id, player_hand=[]):
        self.name = player_name
        self.stack = player_stack
        self.id = player_id  # position sur la table
        self.hand = player_hand
        self.on_going_bet = 0

    def speaks(self, mise):
        player_action = ''
        while player_action not in ['f', 'c', 'r']:
            player_action = input(f"{self.name}, {mise} : call (c), raise (r), fold (f) ?\n")
        if player_action == 'c':
            bet = mise
        elif player_action == 'r':
            raise_val = int(input('Raise = '))
            bet = raise_val
        else:
            bet = 0
        self.stack -= bet - self.on_going_bet
        self.on_going_bet = bet
        print(f"{self.name} " + {'c': 'calls', 'r': 'raises', 'f': 'folds'}[player_action] + f" and bets {bet}.")
        return player_action, bet

class Card:

    def __init__(self, card_value, card_suit):
        self.suit = card_suit
        self.value = card_value

    dic_values = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'Jack', 12: 'Queen', 13: 'King', 14: 'Ace'}
    dic_suits = {0: 'clubs', 1: 'diamonds', 2: 'hearts', 3: 'spades'}

    def __str__(self):
        return Card.dic_values[self.value] + ' of ' + Card.dic_suits[self.suit]

class Table:

    def __init__(self, table_players, small_blind, big_blind):
        self.players = table_players
        self.nb_players = len(self.players)
        self.r_players = self.players
        self.r_players_id = list(
            range(self.nb_players))  # liste des indices des joueurs toujours en jeu dans cette main
        self.sb = small_blind
        self.bb = big_blind
        self.deck = None
        self.cards = []
        self.pot = 0
        self.id_dealer = 0  # l'indice du dealer

    def __iter__(self):
        for player in self.r_players[self.id_speaker:] + self.r_players[:self.id_speaker]:
            # à chaque début de round, le premier joueur parle, ensuite on appelle la méthode playersSpeak, qui va
            # interroger tous les joueurs sauf celui qui vient de miser
            yield player

    def new_hand(self):
        self.r_players = self.players  # remaining players
        for player in self.players:
            player.hand = []
        self.id_dealer = (self.id_dealer + 1) % self.nb_players
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.pot = 0
        self.cards = []
        self.deck = Deck()

    def reboot_id_speaker(self):
        d_from_dealer = [id - self.id_dealer if id > self.id_dealer else inf if id == self.id_dealer
                else self.nb_players - self.id_dealer + id for id in self.r_players_id]
        self.id_speaker = self.r_players_id[d_from_dealer.index(min(d_from_dealer))]

    def hand(self):
        self.new_hand()
        for round in [self.preFlop, self.flop, self.turn_river, self.turn_river]:
            if round():
                self.new_hand()

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            self.players[self.id_speaker].stack -= [self.sb, self.bb][i]
            print(f"{self.players[self.id_speaker].name} bets {[self.sb, self.bb][i]}")
            self.players[self.id_speaker].on_going_bet += [self.sb, self.bb][i]
            self.id_speaker = (self.id_speaker + 1) % self.nb_players
        self.pot = self.sb + self.bb

    def preFlop(self):
        print(f'Dealer : {self.id_dealer}', f"Speaker : {self.id_speaker}", sep='\n')
        self.deal_and_blinds()
        print(self.playersSpeak(self.bb))

    def flop(self):
        self.reboot_id_speaker()
        self.cards += [self.deck.deal() for i in range(3)]
        print([str(card) for card in self.cards])
        self.playersSpeak()

    def turn_river(self):
        self.reboot_id_speaker()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        self.playersSpeak()


    def playersSpeak(self, mise=0, raiser=False):

        if mise == 0:  # signifie qu'on est en début de round
            for player in self.players:
                player.on_going_bet = 0

        if len(self.r_players) > 1:
            for player in self:
                if player == raiser:
                    return
                previous_ogb = player.on_going_bet
                bet = player.speaks(mise)
                self.id_speaker = self.r_players_id[
                    (self.r_players_id.index(self.id_speaker) + 1) % len(self.r_players_id)]
                self.pot += bet[1] - previous_ogb
                if bet[0] == 'r':  # bet renvoie (type, value) ex: ('c', 400)
                    self.playersSpeak(bet[1], raiser=player)
                    return
                elif bet[0] == 'f':
                    self.r_players.remove(player)  # cette liste est nécessaire (pour le moment) pour l'itérateur de la
                    # classe table
                    self.r_players_id.remove(player.id)
        else:
            self.r_players[0].stack += self.pot
            return True

if __name__ == '__main__':
    names = ['Bond', 'DiCaprio', 'Scoubidou', 'B2oba', 'Vigéral', 'Onéla']
    n = len(names)
    players = [Player(player_name=names[i], player_stack=100, player_id=i) for i in range(n)]
    table = Table(players, 5, 10)
    table.hand()



