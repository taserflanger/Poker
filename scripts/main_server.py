import socket

# import pandas as pd
from server.tournoi import Tournoi

# from cash_game import CashGame

SERVER = "178.79.165.80"
LOCAL = "localhost"
PORT = int(input('PORT : '))
N_BOT_MATHEUX=int(input('NBR BOT MATHEUX : '))
N_BOT_DARWIN=int(input('NBR BOT DARWIN : '))
MODE = SERVER

def tournoi(joueur_par_table, stack_initial, sb, bb, nbr_bot):
    t = Tournoi(serveur, joueur_par_table, stack_initial, sb, bb, nbr_bot_matheux, nbr_bot_darwin)
    t.lancer_tournoi()


if __name__ == '__main__':
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind((MODE, PORT))
    serveur.listen(5)

    # fichier_data=pd.read_csv("data.csv", sep=",")

    """
    def cash_game(joueur_par_table, stack_initial, sb, bb, nbr_bot, data ):
        cash_game=CashGame(serveur, joueur_par_table, stack_initial, sb, bb, nbr_bot, data)
        cash_game.launch()
    """

    # tournoi(4, 500, 5, 10, 2)
    tournoi(7, 500, 5, 10, N_BOT_MATHEUX, N_BOT_DARWIN)
    serveur.close()
