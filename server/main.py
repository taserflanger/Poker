from player import Player
from table import Table

def main(GUI=False):
    """rajout de cette fonction pour qu'on puisse l'appeler d'un autre fichier (GUI par exemple)"""
    names = ['Bond', 'DiCaprio', 'Scoubidou', 'B2oba', 'Vigéral', 'Onéla']
    n = len(names)
    players = [Player(player_name=names[i], player_stack=100, player_id=i) for i in range(n)]
    table = Table(players, 5, 10)
    if GUI:
        return table
    table.set()
    for player in table.players:
        print(player.stack)

if __name__ == '__main__':
    main()

