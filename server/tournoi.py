import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import ready, repartion_joueurs_sur_tables, supprimer_thread
from table import Table
from player import Player

#TODO: gerer une deconnexion de force d'un client
        
def gerer_table(table):
    table.game()
        
class Tournoi: #self.n_max est le nombre maximal de joueur par table
    
    def __init__(self, serveur, n_max, stack, small_blind, big_blind):
        self.liste_noms=[]
        self.players=[]
        self.n_max=n_max
        self.stack=stack
        self.serveur=serveur
        self.tables=[]
        self.sb=small_blind
        self.bb=big_blind
        self.thread_table={}
        self.thread_client={}


    def lancer_tournoi(self):
        self.connexion_des_joueurs()
        repartion=repartion_joueurs_sur_tables(len(self.players), self.n_max)
        self.remplir_tables(repartion)


    def connexion_des_joueurs(self):
        while not ready(self.players) or len(self.players) < 2:  
            connexions_demandees, wlist, xlist = select.select([self.serveur], [], [], 0.05)
            for connexion in connexions_demandees:
                client, infos_client = connexion.accept()  
                nouveau_joueur=Player("nom_provisioire", self.stack) 
                nouveau_joueur.connexion=client
                nouveau_joueur.infos_connexion=infos_client    
                nouveau_joueur.tournoi=self
                self.players.append( nouveau_joueur )
                self.thread_client[str(client)]=threading.Thread(None, self.ask_ready_and_name, None, (nouveau_joueur) , {})
                self.thread_client[str(client)].start()
   

    def remplir_tables(self, repartition_):
        marqueur=0
        for taille_table in repartition_:
            self.créer_table(self.players[marqueur : marqueur+taille_table])
            marqueur+=taille_table


    def créer_table(self, joueurs):
        nouvelle_table=Table(joueurs, self.sb, self.bb)  # qui contient les joueurs de marqueurs à marqueurs + i
        for joueur in nouvelle_table.players:
                joueur.table=nouvelle_table
        self.tables.append(nouvelle_table)
        self.thread_table[str(nouvelle_table)]=threading.Thread(None, gerer_table, None, (nouvelle_table), {})
        self.thread_table[str(nouvelle_table)].start()

    def supprimer_table(self, table): 
        self.tables.remove(table)
        supprimer_thread(self.thread_table[ str(table) ])
        del self.thread_table[ str(table) ]
        del table

    def supprimer_joueur(self, joueur):
        self.players.remove(joueur)
        joueur.connexion.close()
        supprimer_thread(self.thread_client[ str(joueur.connexion) ])
        del self.thread_client[ str(joueur.connexion) ]
        del joueur
               
        





        
    def ask_ready_and_name(self, joueur): 
        joueur.connexion.settimeout(60)  #on laisse 1 min pour que le joueur donne son nom
        joueur.name=self.ask_name(joueur)
        client=joueur.connexion
        self.liste_noms.append(joueur.name)
        msg_reçu=b""
        while msg_reçu!= b"yes":
            msg_envoie= str( "Il y a", len(self.players), "joueurs connectés", "\n Etes vous prêts?")
            client.send(msg_envoie.encode())
            try: 
                msg_reçu=client.recv(1024).decode()
                if msg_reçu == "no":
                    client.send("En attente d'autres joueurs...".encode())
                    time.sleep(5)
                elif msg_reçu != "yes":
                    client.send("Erreur, votre saisi est incorrecte".encode())
            except:
                self.supprimer_joueur(joueur)
                msg_reçu=b"yes"  #s'avère inutle car supp detruit le thread en cours

        joueur.connexion.settimeout(30)  # pour la suite on laisse 30 seconde au joueur pour faire une action
        joueur.ready=True
        client.send("La partie va commencer! (attendez qq instants que les autres joueurs soient prêts) ".encode())

    def ask_name(self, joueur):   #on peut ajouter une confirmation
        client=joueur.connexion
        client.send("C'est quoi ton blase?".encode())
        try:
            msg_reçu=client.recv(1024).decode()
            while msg_reçu in self.liste_noms + [""] :  #il faut que le nom du joueur soit != ""
                client.send("Ce nom est déja pris ou n'est pas assez long, saisi un nouveau nom: ".encode())
                try:
                    msg_reçu=client.recv(1024).decode()
                except:
                    self.supprimer_joueur(joueur)
            return msg_reçu
        except:
            self.supprimer_joueur(joueur)
    