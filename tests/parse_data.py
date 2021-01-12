# %%
import re

import numpy as np
import tensorflow as tf

# On représente une carte par son indice dans le paquet 14*couleur + valeur
# Un changement vers flop, turn, river est représenté par la même action que le joueur précédent
# sauf qu’on a dévoilé les cartes (d’où l’intérêt de mettre le ongoingbetet pas la mise ajoutée)

# structure d’un history unit:
# distance to dealer
# action
# amount
# card1 (en main)
# card2
# card1 (sur la table) (-1 si pas encore découverte)
# ...
# card5

# %%
VALUES = ["c", "d", "h", "s"]


def parse_card(s):
    value, color = s[0], s[1]
    try:
        value = int(value)
    except ValueError:
        value = {"T": 10, "A": 14, "J": 11, "Q": 12, "K": 13}[value]

    return value + 14 * VALUES.index(color)


def get_history_from_file(file_name):
    def add_history_unit(hu):
        history.append(np.array(hu, dtype="float32"))

    history = [np.array([-1 for _ in range(10)])]

    with open(f"../server/data/pluribus_databse/out/{file_name}.txt") as file:
        players = []
        ongoingbets = []
        cards = []
        shown_cards = []
        for s in file:
            line = s.split()
            if len(line) == 0:
                continue
            if line[0] == "PokerStars":
                players = []
                cards = []
                shown_cards = []
                continue
            if line[0] == "Seat":
                players.append(line[2])
                ongoingbets.append(0)
            if line[0] == "Dealt":
                card1: str = line[-2][1:]
                card2: str = line[-1][:-1]
                cards.append((parse_card(card1), parse_card(card2)))
            if re.match(r"\*\*\* (TURN|FLOP|RIVER)", s) is not None:
                match = re.findall(r'\[.*?]', s)
                strings = " ".join(map(lambda string: string[1:-1], match)).split()
                shown_cards = list(map(parse_card, strings))
                history_unit = history[-1][:]
                for i in range(-5, -5 + len(shown_cards)):
                    # remplacer les cartes montrées
                    history_unit[i] = shown_cards[i + 5]
                add_history_unit(history_unit)
            if line[0][:-1] in players:
                player = line[0][:-1]
                player_idx = players.index(player)
                action = line[1][0]
                if action == "p" or action == "s":
                    # on ignore les blindes (puts blind) et les showdown
                    # showdown
                    continue
                action = "r" if action == "b" else action
                amount = 0
                if line[1][0] == "calls" or action == "r":
                    amount = float(line[2])
                    ongoingbets[player_idx] += amount
                distance_to_dealer = ((player_idx - 1) % (len(players)))
                history_unit = [
                    distance_to_dealer,
                    ["r", "c", "f"].index(action),
                    amount,
                    cards[player_idx][0],
                    cards[player_idx][1],
                    *(shown_cards + [-1 for _ in range(5 - len(shown_cards))])  # doit rester le dernier
                ]
                add_history_unit(history_unit)

    y = np.asarray(history)[:, :3]
    history = np.asarray(history)[1:]

    return history, y
# %%
database = []
Y = []

for i in range(30, 119):
    for j in "", "b":
        try:
            history, y = get_history_from_file(
                f"pluribus_{i}{j}"
            )
            database.append(history)
            Y.append(y)
        except FileNotFoundError:
            pass
            # certains fichiers n’existent pas

database = np.asarray(database)
Y = np.asarray(Y)
#%%
model = tf.keras.layers.LSTM(3)
layer1 = tf.keras.layers.Conv1D((92, None))
