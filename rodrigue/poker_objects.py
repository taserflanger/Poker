"""
L'itérateur de la classe table permet de parcourir les joueurs restant dans la main, à partir de celui qui doit parler
en premier.
Pour jouer une main:

TODO:   - s'occuper de la fonctionnalité fold, et de l'attribut ind_speaker
        - s'occuper du cas de figure ou tout le monde sauf 1 s'est couché
        - retranscrire dans un modèle client/serveur, où le client n'a accès qu'aux informations qui le concernent
        - (détail: Si un joueur n'a pas assez d'argent pour faire sa blinde, il doit être exclu au début)

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

    def speaks(self, amount_to_call):
        player_action = ''
        diff = amount_to_call - self.on_going_bet
        c = "call"
        bet = 0
        raise_val = 0
        if diff == 0: c = "check"
        while player_action not in ['f', 'c', 'r']:
            player_action = input(f"{self.name}, {amount_to_call} : {c} (c), raise (r), fold (f) ?\n")
        if player_action == 'c':
            # TODO: - détecter lorsqu'un raise/call est un all-in. Faire en sorte qu'on ne peut pas gagner trop lorsqu'on
            #       - se met all-in avec pas grand chose (selon les variantes c'est plus ou moins strict je crois)
            if diff > self.stack:
                print("all-in!")
                diff = self.stack
            bet = diff
        elif player_action == 'r':
            raise_val = float("inf")
            while raise_val > self.stack:
                raise_val = int(input('Raise = '))
            bet = raise_val + diff
        self.stack -= bet
        self.on_going_bet += bet
        print(f"{self.name} " + {'c': 'calls', 'r': 'raises', 'f': 'folds'}[player_action] + f" and bets {bet}.")
        return player_action, raise_val


class Card:

    def __init__(self, card_value, card_suit):
        self.suit = card_suit
        self.value = card_value

    dic_values = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'Jack', 12: 'Queen',
                  13: 'King', 14: 'Ace'}
    dic_suits = {0: 'clubs', 1: 'diamonds', 2: 'hearts', 3: 'spades'}

    def __str__(self):
        return Card.dic_values[self.value] + ' of ' + Card.dic_suits[self.suit]


class Table:

    def __init__(self, table_players, small_blind, big_blind, dealer="random"):
        self.nb_players = len(table_players)
        self.players = table_players
        self.nb_players = len(self.players)
        if dealer == "random":
            self.id_dealer = random.randint(0, self.nb_players - 1)
        else:
            self.id_dealer = dealer
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.active_players = [True for _ in range(self.nb_players)]
        self.sb = small_blind
        self.bb = big_blind
        self.deck = Deck()
        self.cards = []
        self.pot = 0
        self.id_dealer = 0  # l'indice du dealer

    def __iter__(self):
        i = (self.id_dealer + 1) % self.nb_players
        for k in range(self.nb_players):
            yield (i + k) % self.nb_players
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

    def next_player_id(self, id):
        next_id = (id + 1) % self.nb_players
        while not self.active_players[next_id]:
            next_id = (next_id + 1) % self.nb_players
        return next_id

    def initialise_round(self):
        for player in self.players:
            self.pot += player.on_going_bet
            player.on_going_bet = 0
        self.id_speaker = self.next_player_id(self.id_dealer)

    def hand(self):
        self.new_hand()
        for round in [self.preFlop, self.flop, self.turn_river, self.turn_river]:
            winner_id = round()
            if winner_id:
                break
        print(f"{self.players[winner_id].name} wins")

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.hand.append(self.deck.deal())
        for i in range(2):
            print(f"{self.players[self.id_speaker].name} bets {[self.sb, self.bb][i]}")
            self.players[self.id_speaker].on_going_bet += [self.sb, self.bb][i]
            self.id_speaker = self.next_player_id(self.id_speaker)

    def preFlop(self):
        print(f'Dealer : {self.id_dealer}', f"Speaker : {self.id_speaker}", sep='\n')
        self.deal_and_blinds()
        return self.playersSpeak(self.bb)

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for i in range(3)]
        print([str(card) for card in self.cards])
        return self.playersSpeak()

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        return self.playersSpeak()

    def playersSpeak(self, mise=0):
        for _ in range(self.nb_players):
            speaker = self.id_speaker
            if sum(self.active_players) == 1:
                winner_id = self.next_player_id(
                    speaker)  # on trouve le dernier joueur restant (qui est aussi le suivant)
                return winner_id
            if not self.active_players[speaker]:
                continue
            dealer = self.id_dealer

            action, amount = self.players[self.id_speaker].speaks(mise)
            if speaker == dealer and self.players[self.next_player_id(dealer)].on_going_bet == mise:
                # si personne n'a relancé dans le tour, on passe à l'étape suivante.
                return
            if action == "f":
                self.active_players[speaker] = False
            self.id_speaker = self.next_player_id(self.id_speaker)
            mise += amount


if __name__ == '__main__':
    names = ['Bond', 'DiCaprio', 'Scoubidou', 'B2oba', 'Vigéral', 'Onéla']
    n = len(names)
    players = [Player(player_name=names[i], player_stack=100, player_id=i) for i in range(n)]
    table = Table(players, 5, 10)
    table.hand()
