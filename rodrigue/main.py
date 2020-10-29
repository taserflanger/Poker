from rodrigue.player import Player
from rodrigue.table import Table

if __name__ == '__main__':
    names = ['Bond', 'DiCaprio', 'Scoubidou', 'B2oba', 'Vigéral', 'Onéla']
    n = len(names)
    players = [Player(player_name=names[i], player_stack=100, player_id=i) for i in range(n)]
    table = Table(players, 5, 10)
    table.hand()
