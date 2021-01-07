import socket

# import pandas as pd
from classes.tournoi import Tournoi

# from cash_game import CashGame
serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

adresse_serveur_linode = "178.79.165.80"
adresse_serveur_local = ""
serveur.bind((adresse_serveur_local, 12800))
serveur.listen(5)


# fichier_data=pd.read_csv("data.csv", sep=",")
def tournoi(joueur_par_table, stack_initial, sb, bb, nbr_bot):
    t = Tournoi(serveur, joueur_par_table, stack_initial, sb, bb, nbr_bot)
    t.lancer_tournoi()


"""
def cash_game(joueur_par_table, stack_initial, sb, bb, nbr_bot, data ):
    cash_game=CashGame(serveur, joueur_par_table, stack_initial, sb, bb, nbr_bot, data)
    cash_game.launch()
"""

# tournoi(4, 500, 5, 10, 2)
tournoi(4, 500, 5, 10, 5)
serveur.close()
