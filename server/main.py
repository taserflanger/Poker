from player import Player
from table import Table

if __name__ == '__main__':
    names = ['Bond', 'DiCaprio', 'Scoubidou', 'B2oba', 'Vigéral', 'Onéla']
    n = len(names)
    money = [1000, 100, 50, 500, 30, 100]
    players = [Player(player_name=names[i], player_stack=money[i], player_id=i) for i in range(n)]
    table = Table(players, 5, 10)
    table.set()
