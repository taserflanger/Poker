import socket
from tournoi import Tournoi
serveur=socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
serveur.bind(("", 50000))  
serveur.listen(5)  

def tournoi(joueur_par_table, stack_initial):
    tournoi=Tournoi(serveur, joueur_par_table, stack_initial)
    tournoi.lancer_tournoi()

serveur.close()