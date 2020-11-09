import socket
import threading
import select
import time
import json
from fonctions_serveur import ready, repartion_joueurs_sur_tables
from table import Table
from player import Player

        

def gerer_table(table):
    table.game()
        
class Tournoi(): #self.n_max est le nombre maximal de joueur par table
    
    def __init__(self, serveur, n_max, stack):
        self.liste_noms=[]
        self.players=[]
        self.n_max=n_max
        self.stack=stack
        self.serveur=serveur
    
    def ask_ready_and_name(self, joueur): 
        joueur.name=self.ask_name(joueur)
        client=joueur.connexion
        self.liste_noms.append(joueur.name)
        msg_reçu=b""
        while msg_reçu!= b"yes":
            msg_envoie= str( "Il y a", len(self.players), "joueurs connectés", "\n Etes vous prêts?")
            client.send(msg_envoie.encode())
            msg_reçu=client.recv(1024).decode()
            if msg_reçu == "no":
                client.send("En attente d'autres joueurs...".encode())
                time.sleep(5)
            elif msg_reçu != "yes":
                client.send("Erreur".encode())
        joueur.ready=True
        client.send("La partie va commencer! (attendez qq instants que les autres joueurs soient prêts) ".encode())

    def ask_name(self, joueur):   #on peut ajouter une confirmation
        client=joueur.connexion
        client.send("C'est quoi ton blase?".encode())
        msg_reçu=client.recv(1024).decode()
        while msg_reçu in self.liste_noms + [""] :  #il faut que le nom du joueur soit != ""
            client.send("Ce nom est déja pris ou n'est pas assez long, saisi un nouveau nom: ".encode())
            msg_reçu=client.recv(1024).decode()
        return msg_reçu
    
    
    def remplir_tables(self, repartition_):
        tables_du_tournoi=[]
        marqueur=0
        for taille_table in repartition_:
            nouvelle_table=Table(self.players[marqueur : marqueur+taille_table], 5, 10)  # qui contient les joueurs de marqueurs à marqueurs + i
            marqueur+=taille_table
            tables_du_tournoi.append(nouvelle_table)
        return tables_du_tournoi

    def lancer_tournoi(self):
        self.connexion_des_joueurs()
        repartion=repartion_joueurs_sur_tables(len(self.players), self.n_max)
        table_tournoi=self.remplir_tables(repartion)
        thread_table=[]
        for table in table_tournoi:
            thread_table.append(threading.Thread(None, gerer_table, None, (table), {}))
            thread_table[-1].start()
    
    def connexion_des_joueurs(self):
        thread_client=[]
        while not ready(self.players) or len(self.players) < 2:  
            connexions_demandees, wlist, xlist = select.select([self.serveur], [], [], 0.05)
            for connexion in connexions_demandees:
                client, infos_client = connexion.accept()  
                nouveau_joueur=Player("nom_provisioire", self.stack) 
                nouveau_joueur.connexion=client
                nouveau_joueur.infos_connexion=infos_client    
                self.players.append( nouveau_joueur )
                thread_client.append(threading.Thread(None, self.ask_ready_and_name, None, (nouveau_joueur) , {}))
                thread_client[-1].start()
   


