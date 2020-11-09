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
    thread=[]

    def ask_ready_and_name(joueur, nbr_joueurs_connectés): # on peut remplacer nbr_joueur_connecté par len(liste_noms) ou len(players) pour que se soit actualisé
        joueur.name=ask_name(joueur)
        liste_noms.append(joueur.name)
        msg_envoie= str( "Il y a", nbr_joueurs_connectés, "joueurs connectés", "\n Etes vous prêts?")
        client.send(msg_envoie.encode())
        msg_reçu=b""
        while msg_reçu!= b"yes":
            msg_reçu=client.recv(1024).decode()
            if msg_reçu == "no":
                client.send("En attente d'autres joueurs...".encode())
                time.sleep(5)
                msg_envoie= str( "Il y a", nbr_joueurs_connectés, "joueurs connectés", "\n Etes vous prêts?")
            elif msg_reçu != "yes":
                client.send("Erreur".encode())
        client.send("La partie va commencer! (attendez qq instants que les autres joueurs soient prêts) ".encode())

    def ask_name(joueur):   #on peut ajouter une confirmation
        client=joueur.connexion
        client.send("C'est quoi ton blase?")
        msg_reçu=client.recv(1024).decode()
        while msg_reçu in liste_noms + [""] :  #il faut que le nom du joueur soit != ""
            client.send("Ce nom est déja pris ou n'est pas assez long, saisi un nouveau nom: ")
            msg_reçu=client.recv(1024).decode()
        return msg_reçu
    
    def gérer_table(table):
        table.game()

    def remplir_tables(repartition_):
        tables_du_tournoi=[]
        marqueur=0
        thread2=[]
        for taille_table in repartition_:
            nouvelle_table=Table(players[marqueur : marqueur+taille_table], 5, 10)  # qui contient les joueurs de marqueurs à marqueurs + i
            marqueur+=taille_table
            tables_du_tournoi.append(nouvelle_table)
            thread2.append(threading.Thread(None, gérer_table, None, (nouvelle_table), {}))
            thread2[-1].start()
        return tables_du_tournoi, thread2


    while not ready(players):  
        connexions_demandees, wlist, xlist = select.select([serveur], [], [], 0.05)
        for connexion in connexions_demandees:
            client, infos_client = connexion.accept()  
            nouveau_joueur=Player("nom_provisioire", stack)     
            players.append( nouveau_joueur )
            players[-1].connexion, players[-1].info_connexion = client , infos_client
            thread.append(threading.Thread(None, ask_ready_and_name, None, (nouveau_joueur, len(players)) , {}))
            thread[-1].start()

    repartion=repartion_joueurs_sur_tables(len(players), n_max)
    remplir_tables(repartion)
    

serveur.close()