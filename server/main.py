from bot.genectic.Bot import Bot
from player import Player
from table import Table
from numpy import array


def main(GUI=False):
    """rajout de cette fonction pour qu'on puisse l'appeler d'un autre fichier (GUI par exemple)"""
    names = ['Bond']
    n = len(names)
    players = [Player(player_name=names[i], player_stack=100) for i in range(n)]

    Params = {"W": None, "b": None, "f": None}

    # read params
    for s in "W", "b", "f":
        with open(f"bot/genectic/{s}.csv") as file:
            Params[s] = eval(file.read())
    for i in range(4):
        players.append(
            Bot(player_name=f"Bot {i}", player_stack=100, sizes=[50], W=Params["W"], b=Params["b"], f=Params["f"]))
    table = Table(players, 5, 10)
    if GUI:
        return table
    table.game()
    for player in table.players:
        print(player.stack)


if __name__ == '__main__':
    main()
