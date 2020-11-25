# -*- coding: utf-8 -*-
import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import repartion_joueurs_sur_tables, supprimer_thread, gerer_table, try_recv, try_send, wait_for_table, give_table_min_max, give_chaises_dispo
from table import Table
from player import Player

#TODO: gerer une deconnexion de force d'un client

        
class Salon: #self.n_max est le nombre maximal de joueur par table
    
    def __init__(self, serveur, n_max, stack, small_blind, big_blind):
        self.liste_noms, self.players, self.tables, self.wait_file=map(list, ([] for _ in range(4)))
        self.n_max=n_max
        self.stack=stack
        self.serveur=serveur
        self.sb, self.bb = small_blind, big_blind
        self.thread_table={}
        self.thread_client={}
        self.started=False
        self.let_modif_thread=True
        self.gap_max=2
   
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
                nouveau_joueur.salon=self
                self.thread_client[str(client)]=threading.Thread(None, self.ask_ready_and_name, None, [nouveau_joueur] , {})
                self.thread_client[str(client)].start()

    def send_len_players(self):
        for player in self.players:
            player.connexion.send(str(len(self.players))).encode("utf-8")
    
    def ask_thread(self):
        """Demande d'autorisation de modification des variables globales: ainsi 2 threads ne peuvent pas modifier les variables globales en meme temps"""
        while not self.let_modif_thread:   
            time.sleep(1)                   
        self.let_modif_thread=False
        
    def ask_ready_and_name(self, joueur): 
        joueur.connexion.settimeout(600)  #on laisse 1 min pour que le joueur donne son nom
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
        msg=try_recv(joueur)
        while msg in self.liste_noms + [""] :  #il faut que le nom du joueur soit != ""
            try_send(joueur, "erreur nom".encode("utf-8"))   #erreur nom correspond à un nom deja pris
            msg=try_recv(joueur)
        try_send(joueur, "ok".encode("utf-8"))
        return msg
   
    def creer_table(self, joueurs):
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

    def remaniement(self):
        print("remaniement")
        table_min, table_max=give_table_min_max(self.tables)
        repartit_tables=[len(table) for table in self.tables]
        if len(table_max) - len(table_min) >= self.gap_max: 
            self.transfert_joueur()
        elif give_chaises_dispo(repartit_tables, self.n_max) - self.n_max >=0: 
            # ie on peut répartir les joueurs d'une des tables sur toutes les autres tables, "étape de redistribution"
            table_min.redistribution=True
            print("redistribution de ", table_min, "au prochain tour")

    def redistribution(self, r_table):
        while not self.let_modif_thread:   # ainsi 2 threads ne peuvent pas faire tourner cette fonction en meme temps
            time.sleep(1)                   # et donc ne se gènent pas lors des modifications des tables
        self.let_modif_thread=False
        r_table.in_change=True
        k=len(r_table)
        self.tables.remove(r_table)
        self.tables.sort(key=lambda table: len(table))
        k=0
        n=len(self.tables)
        #on ajoute un joueur à chaque table de la plus petite à la plus grande et puis on recommence
        while r_table.players:  
            joueur=r_table.players.pop(0)
            self.tables[k].wait_in.append(joueur) # on ajoute le joueur à la liste d'attente de la table
            k= (k+1) % n 
            #ainsi on boucle sur la liste des tables du salon ie quand k==n alors on repart à k==0
        r_table.end=True #supprime la table
        r_table.in_change=False
        self.let_modif_thread=True
    
    #la plus grosse table envoie un joueur à la plus petite
    #on attend tmax est fini le tour pour lui retirer un joueur et l'envoyer sur tbale_min
    #pendant ce temps la table_min attend
    def transfert_joueur(self): 
        print("transfert")
        table_min, table_max=give_table_min_max(self.tables)

        while table_max.in_change:
            time.sleep(0.01)
        if table_max.wait_in:
            joueurchanger=table_max.wait_in.pop(0)  
        else:
            joueurchanger = table_max.players[ randint( 0, len(table_max.players)-1 ) ] #embettant car la vrai taille est table.taille
            # et si ils sont tous discnt? ==> impossible grace au while table.in_change qui assure la suppresion des joueurs disconnected dans table
        
        while table_max.in_game:
            time.sleep(3)
        table_max.in_change=True
        #joueur_à_changer.connexion.send("Vous allez changer de table, patientez un instant".encode()) #mettre un trysend
        table_max.wait_out.append(joueurchanger)
        table_min.wait_in.append(joueurchanger)
        table_max.in_change=False

    #si il y a de la place dans une table, on ajoute le joueur à la table
#sinon on ajoute un joueur d'une table remplie dans la table ou il n'y a plus qu'un joueur
#comme il y a équilibre à toute étape, ce dernier cas n'est possible que si n_max=3 et table_min=1
#alors on se retrouve avec 2 tables de 2 joueurs et le reste de 3 joueurs, il y a équilibre
    def gerer_joueur_seul(self, table, joueur_seul): # si + de 2 tables
        print("gerer_joueur_seul")
        chaise_dispo=[ (True if len(table) < self.n_max else False) for table in self.tables]
        if sum(chaise_dispo) == 1: #s'il n'y a que la table avec 1 joueur dedans  #ie il n'existe pas de table avec une place de libre
        #on effectue un transfert de la table_max à la table_min, ie d'une table remplie à une table ou il n'y a plus qu'un joueur
        #on peut mq que ce cas est unique si self.n_max > 2 et il correspond à 1/3/3/.../3 et qui devient 2/2/3/.../3
            self.transfert_joueur()

        else: # on insere le joueur dans la table qui a une place dispo et on détruit la 1ere table 
            #self.supprimer_table(table)
            self.tables.remove(table)
            table.end=True
            table_min, t=give_table_min_max(self.tables)
            table_min.wait_in.append(joueur_seul)