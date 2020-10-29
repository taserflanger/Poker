from rodrigue.deck import Deck

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

    def new_hand(self):
        for player in self.players:
            player.set = []
        self.id_dealer = (self.id_dealer + 1) % self.nb_players
        self.id_speaker = (self.id_dealer + 1) % self.nb_players
        self.pot = 0
        self.cards = []
        self.deck = Deck()

    def next_player_id(self, player_id):
        next_id = (player_id + 1) % self.nb_players
        while not self.active_players[next_id]:
            next_id = (next_id + 1) % self.nb_players
        return next_id

    def initialise_round(self):
        for player in self.players:
            self.pot += player.on_going_bet
            player.on_going_bet = 0
        self.id_speaker = self.next_player_id(self.id_dealer)

    def set(self):
        self.new_hand()
        for round_ob in [self.pre_flop, self.flop, self.turn_river, self.turn_river]:
            winner_id = round_ob()
            if winner_id:
                break
        print(f"{self.players[winner_id].name} wins")

    def deal_and_blinds(self):
        for player in self.players * 2:
            player.set.append(self.deck.deal())
        for i in range(2):
            print(f"{self.players[self.id_speaker].name} bets {[self.sb, self.bb][i]}")
            self.players[self.id_speaker].on_going_bet += [self.sb, self.bb][i]
            self.id_speaker = self.next_player_id(self.id_speaker)

    def pre_flop(self):
        print(f'Dealer : {self.id_dealer}', f"Speaker : {self.id_speaker}", sep='\n')
        self.deal_and_blinds()
        return self.players_speak(self.bb)

    def flop(self):
        self.initialise_round()
        self.cards += [self.deck.deal() for _ in range(3)]
        print([str(card) for card in self.cards])
        return self.players_speak()

    def turn_river(self):
        self.initialise_round()
        self.cards += [self.deck.deal()]
        print([str(card) for card in self.cards])
        return self.players_speak()

    def players_speak(self, mise=0):
        # Todo: implémenter le tour depuis le raiser
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
