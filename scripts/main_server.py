import socket

# import pandas as pd
from sys import argv

from server import Tournoi

# from cash_game import CashGame

SERVER = "178.79.165.80"
LOCAL = "localhost"
MODE = SERVER
if len(argv) >= 1 and argv[1] == "local":
    MODE = LOCAL
try:
    PORT = int(argv[2])
except (ValueError, IndexError):
    PORT = int(input('PORT : '))
try:
    N_BOT_MATHEUX = int(argv[3])
except (ValueError, IndexError):
    N_BOT_MATHEUX = int(input('NBR BOT MATHEUX : '))
try:
    N_BOT_DARWIN = int(argv[4])
except (ValueError, IndexError):
    N_BOT_DARWIN = int(input('NBR BOT DARWIN : '))




def tournoi(joueur_par_table, stack_initial, sb, bb, nbr_bot_matheux, nbr_bot_darwin):
    t = Tournoi(serveur, joueur_par_table, stack_initial, sb, bb, nbr_bot_matheux, nbr_bot_darwin)
    t.lancer_tournoi()


if __name__ == '__main__':
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind((MODE, PORT))
    serveur.listen(5)

    tournoi(7, 500, 5, 10, N_BOT_MATHEUX, N_BOT_DARWIN)
    serveur.close()
