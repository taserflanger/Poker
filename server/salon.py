import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import repartion_joueurs_sur_tables, supprimer_thread
from table import Table
from player import Player

#TODO: gerer une deconnexion de force d'un client
        
def gerer_table(table):
    table.game()
        
class Salon: #self.n_max est le nombre maximal de joueur par table
    
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
        self.wait_file=[]
        self.start=False
   

    def ready(self):
        return False
        
    def connexion_des_joueurs(self):
        while not self.ready():  
            connexions_demandees, wlist, xlist = select.select([self.serveur], [], [], 1)
            self.send_len_players()
            for connexion in connexions_demandees:
                client, infos_client = connexion.accept()  
                nouveau_joueur=Player("nom_provisioire", self.stack) 
                nouveau_joueur.connexion=client
                nouveau_joueur.infos_connexion=infos_client    
                nouveau_joueur.tournoi=self
                self.thread_client[str(client)]=threading.Thread(None, self.ask_ready_and_name, None, [nouveau_joueur] , {})
                self.thread_client[str(client)].start()
            

    def send_len_players(self):
        for player in self.players:
            player.connexion.send(str(len(self.players))).encode("utf-8")
    

    def ask_ready_and_name(self, joueur): 
        joueur.connexion.settimeout(60)  #on laisse 1 min pour que le joueur donne son nom
        joueur.name=self.ask_name(joueur)
        if not self.start:
            self.liste_noms.append(joueur.name)
            self.players.append( joueur )
            self.wait_file.append(joueur)
            joueur.connexion.recv(1024).decode("utf-8")  #le client envoie "pret", il ne peut rien envoyer d'autre
            joueur.ready=True     
            joueur.connexion.settimeout(30)  # pour la suite on laisse 30 seconde au joueur pour faire une action
        else: # le tournoi a déjà commencé
            self.supprimer_joueur(joueur)

    def ask_name(self, joueur):   #on peut ajouter une confirmation
        client=joueur.connexion
        try:
            msg_reçu=client.recv(1024).decode("utf-8")
            while msg_reçu in self.liste_noms + [""] :  #il faut que le nom du joueur soit != ""
                client.send("erreur nom".encode("utf-8"))   #erreur nom correspond à un nom deja pris
                try:
                    msg_reçu=client.recv(1024).decode("utf-8")
                except:
                    self.supprimer_joueur(joueur)
            return msg_reçu
        except:
            self.supprimer_joueur(joueur)
    


    def créer_table(self, joueurs):
        nouvelle_table=Table(joueurs, self.sb, self.bb)  # qui contient les joueurs de marqueurs à marqueurs + i
        for joueur in nouvelle_table.players:
                joueur.table=nouvelle_table
        self.tables.append(nouvelle_table)
        self.thread_table[str(nouvelle_table)]=threading.Thread(None, gerer_table, None, [nouvelle_table], {})
        self.thread_table[str(nouvelle_table)].start()

    def supprimer_table(self, table): 
        self.tables.remove(table)
        supprimer_thread(self.thread_table[ str(table) ])
        del self.thread_table[ str(table) ]
        del table

    def supprimer_joueur(self, joueur):
        joueur.connexion.close()
        supprimer_thread(self.thread_client[ str(joueur.connexion) ])
        del self.thread_client[ str(joueur.connexion) ]
        del joueur
               