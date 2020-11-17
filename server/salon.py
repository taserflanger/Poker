import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import repartion_joueurs_sur_tables, supprimer_thread, gerer_table, try_recv, try_send, wait_for_table, give_table_min_max, determiner_joueurs_mal_repartis
from table import Table
from player import Player

#TODO: gerer une deconnexion de force d'un client

        
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
        self.started=False
        self.let_modif_thread=True
   

    def ready(self):
        return False
        
    def connexion_des_joueurs(self):
        while not self.ready():  
            connexions_demandees, wlist, xlist = select.select([self.serveur], [], [], 0.05)
            #self.send_len_players()
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
        if not self.started:
            self.liste_noms.append(joueur.name)
            self.players.append( joueur )
            self.wait_file.append(joueur)
            try_recv(joueur) #le client envoie "pret", il ne peut rien envoyer d'autre
            joueur.ready=True     
            joueur.connexion.settimeout(300)  # pour la suite on laisse 30 seconde au joueur pour faire une action
        else: # le tournoi a déjà commencé, marche aussi en cash game car self.started=False tout le temps
            self.supprimer_joueur(joueur)

    def ask_name(self, joueur):   #on peut ajouter une confirmation
        try_send(joueur, "preparation".encode("utf-8"))
        msg_reçu=try_recv(joueur)
        while msg_reçu in self.liste_noms + [""] :  #il faut que le nom du joueur soit != ""
            try_send(joueur, "erreur nom".encode("utf-8"))   #erreur nom correspond à un nom deja pris
            msg_reçu=try_recv(joueur)
        try_send(joueur, "ok".encode("utf-8"))
        return msg_reçu
   
    def créer_table(self, joueurs):
        nouvelle_table=Table(joueurs, self.sb, self.bb)  # qui contient les joueurs de marqueurs à marqueurs + i
        for joueur in nouvelle_table.players:
                joueur.table=nouvelle_table
        self.tables.append(nouvelle_table)
        self.thread_table[str(nouvelle_table)]=threading.Thread(None, gerer_table, None, [nouvelle_table], {})
        self.thread_table[str(nouvelle_table)].start()

    def supprimer_table(self, table): 
        #self.tables.remove(table)
        table.end=True
        #del table

    def supprimer_joueur(self, joueur):
        #supprimer_thread(self.thread_client[ str(joueur.connexion) ])
        #del self.thread_client[ str(joueur.connexion) ]
        joueur.connexion.close()
        #del joueur
