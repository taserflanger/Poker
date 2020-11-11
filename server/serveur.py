import socket
from tournoi import Tournoi
serveur=socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
adresse_serveur=""
#adresse_serveur=""
serveur.bind((adresse_serveur, 12800))  
serveur.listen(5)  

def tournoi(joueur_par_table, stack_initial, sb, bb):
    tournoi=Tournoi(serveur, joueur_par_table, stack_initial, sb, bb)
    tournoi.lancer_tournoi()

tournoi(3, 500, 5, 10)
serveur.close()