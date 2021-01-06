# -*- coding: utf-8 -*-
import socket
#import pandas as pd
from tournoi import Tournoi
#from cash_game import Cash_game
serveur=socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

adresse_serveur_linode="178.79.165.80"
adresse_serveur_local = ""
serveur.bind((adresse_serveur_linode, 12800))
serveur.listen(5)  
#fichier_data=pd.read_csv("data.csv", sep=",")
def tournoi(joueur_par_table, stack_initial, sb, bb, nbr_bot):
    tournoi=Tournoi(serveur, joueur_par_table, stack_initial, sb, bb, nbr_bot)
    tournoi.lancer_tournoi()

"""
def cash_game(joueur_par_table, stack_initial, sb, bb, nbr_bot, data ):
    cash_game=Cash_game(serveur, joueur_par_table, stack_initial, sb, bb, nbr_bot, data)
    cash_game.launch()
"""
    
#tournoi(4, 500, 5, 10, 2)
tournoi(4, 500, 5, 10, 0)
serveur.close()