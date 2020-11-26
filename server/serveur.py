# -*- coding: utf-8 -*-
import socket
from tournoi import Tournoi
serveur=socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

adresse_serveur_linode="178.79.165.80"
adresse_serveur_local=""
serveur.bind((adresse_serveur_local, 12800))  
serveur.listen(5)  

def tournoi(joueur_par_table, stack_initial, sb, bb):
    tournoi=Tournoi(serveur, joueur_par_table, stack_initial, sb, bb)
    tournoi.lancer_tournoi()

tournoi(4, 500, 5, 10)
serveur.close()