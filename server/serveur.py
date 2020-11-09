import socket
import threading
import select
import time
import json
from fonctions_serveur import ready, repartion_joueurs_sur_tables
from table import Table
from player import Player

serveur=socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
serveur.bind(("", 50000))  
serveur.listen(5)          

        
def tournois(n_max, stack): #n_max est le nombre maximal de joueur par table
    liste_noms=[]
    players=[]
    thread_client=[]

    def ask_ready_and_name(joueur): # on peut remplacer nbr_joueur_connecté par len(liste_noms) ou len(players) pour que se soit actualisé
        joueur.name=ask_name(joueur)
        liste_noms.append(joueur.name)
        msg_reçu=b""
        while msg_reçu!= b"yes":
            msg_envoie= str( "Il y a", len(players), "joueurs connectés", "\n Etes vous prêts?")
            client.send(msg_envoie.encode())
            msg_reçu=client.recv(1024).decode()
            if msg_reçu == "no":
                client.send("En attente d'autres joueurs...".encode())
                time.sleep(5)
            elif msg_reçu != "yes":
                client.send("Erreur".encode())
        joueur.ready=True
        client.send("La partie va commencer! (attendez qq instants que les autres joueurs soient prêts) ".encode())

    def ask_name(joueur):   #on peut ajouter une confirmation
        client=joueur.connexion
        client.send("C'est quoi ton blase?".encode())
        msg_reçu=client.recv(1024).decode()
        while msg_reçu in liste_noms + [""] :  #il faut que le nom du joueur soit != ""
            client.send("Ce nom est déja pris ou n'est pas assez long, saisi un nouveau nom: ".encode())
            msg_reçu=client.recv(1024).decode()
        return msg_reçu
    
    def gerer_table(table):
        table.game()

    def remplir_tables(repartition_):
        tables_du_tournoi=[]
        marqueur=0
        for taille_table in repartition_:
            nouvelle_table=Table(players[marqueur : marqueur+taille_table], 5, 10)  # qui contient les joueurs de marqueurs à marqueurs + i
            marqueur+=taille_table
            tables_du_tournoi.append(nouvelle_table)
        return tables_du_tournoi

    def lancer_tournoi(n_max):
        repartion=repartion_joueurs_sur_tables(len(players), n_max)
        table_tournoi=remplir_tables(repartion)
        thread_table=[]
        for table in table_tournoi:
            thread_table.append(threading.Thread(None, gerer_table, None, (table), {}))
            thread_table[-1].start()
    
    while not ready(players) or len(players) < 2:  
        connexions_demandees, wlist, xlist = select.select([serveur], [], [], 0.05)
        for connexion in connexions_demandees:
            client, infos_client = connexion.accept()  
            nouveau_joueur=Player("nom_provisioire", stack) 
            nouveau_joueur.connexion=client
            nouveau_joueur.infos_connexion=infos_client    
            players.append( nouveau_joueur )
            thread_client.append(threading.Thread(None, ask_ready_and_name, None, (nouveau_joueur) , {}))
            thread_client[-1].start()

    lancer_tournoi(n_max)
   

serveur.close()