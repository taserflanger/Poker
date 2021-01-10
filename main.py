from server.bot.genectic.BotGenetic import Bot
from server.player import Player
from server.table import Table


def main(GUI=False):
    """rajout de cette fonction pour qu'on puisse l'appeler d'un autre fichier (GUI par exemple)"""
    names = ['Bond', 'Salut', 'Pascal', 'Andres', 'Rodrigue']
    n = len(names)
    players = [Player(player_name=names[i], player_stack=100) for i in range(n)]

    table = Table(players, 5, 10)
    if GUI:
        return table
    table.game()
    for player in table.players:
        print(player.stack)


if __name__ == '__main__':
    main()
