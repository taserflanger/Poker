# -*- coding: utf-8 -*-
import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import del_thread, gerer_table, try_recv, try_send, wait_for_table, give_table_min_max, give_chaises_dispo
from table import Table
from player import Player
from bot_proba import Bot_matheux
import fonctions_table as ft

#TODO: gerer une deconnexion de force d'un client

        
class Salon: #self.n_max est le nombre maximal de player par table
    
    def __init__(self, serveur, n_max, stack, small_blind, big_blind, nbr_bot):
        self.liste_names, self.players, self.tables, self.wait_file=map(list, ([] for _ in range(4)))
        self.n_max=n_max
        self.stack=stack
        self.serveur=serveur
        self.sb, self.bb = small_blind, big_blind
        self.thread_table={}
        self.thread_client={}
        self.started=False
        self.let_modif_thread=True
        self.gap_max=2
        self.nbr_bot=nbr_bot
   
    def ready(self):  #cette fonction est redéfinie dans tournoi, mais ne l'est pas dans cashgame on ne veut pas que les attentes de connexions s'arretent
        return False
        
    def players_connexion(self):
        """gère la connexion des sockets clients au socket server"""
        print("ouverture des connexions au salon")
        while not self.ready():  
            connexions_demandees = select.select([self.serveur], [], [], 0.05)[0]
            for connexion in connexions_demandees:
                client, infos_client = connexion.accept()  
                new_player=Player("nom_provisioire", self.stack) 
                new_player.connexion=client
                new_player.infos_connexion=infos_client    
                new_player.salon=self
                self.thread_client[str(client)]=threading.Thread(None, self.gerer_preparation, None, [new_player] , {})
                self.thread_client[str(client)].start()
                
                    
        print("fermeture des connexions au Salon")
        #à mettre autre part car pour le cashgame ça marche pas...
        for i in range(self.nbr_bot):
            bot_name="bot_"+str(i)
            new_bot=Bot_matheux(bot_name, self.stack)
            new_bot.salon=self
            self.players.append( new_bot )
            self.wait_file.append(new_bot)
  
    def ask_thread(self):
        """Demande d'autorisation de modification des variables globales: 
            ainsi 2 threads ne peuvent pas modifier les variables globales en meme temps"""
        while not self.let_modif_thread:   
            time.sleep(1)                   
        self.let_modif_thread=False
        
    def gerer_preparation(self, player):
        """phase de demande du nom au client avant lancement du tournoi"""
        try:
            for _ in range(2):
                infos=try_recv(player)
                msg=json.loads(infos)
                if msg["flag"]=="name":
                    name=msg['name']
                    self.ask_name(player, name)
                elif msg["flag"]=="ready":
                    self.wait_file.append(player) 
                    player.ready=True  
        except:
            print("exception3 player disconnected")
            self.del_player(player)
            try: 
                self.liste_names.remove(player.name)
                self.players.remove(player)
            except:
                print("exeption2")
                

    def ask_name(self, player, name):   
        while name in self.liste_names + [""] + ["f"]  : 
            try_send(player, {"flag":"error name", "test":{"and": [1,2]}})  
            msg=json.loads(try_recv(player))
            if msg["flag"]=="name":
                name=msg["name"]
        try_send(player, {"flag": "name ok"})
        player.name=name
        #player.connexion.settimeout(30)
        if not self.started and player.name!="f":
            self.liste_names.append(player.name)
            self.players.append(player)
        else: # le tournoi a déjà commencé, marche aussi en cash game car self.started=False tout le temps
            self.del_player(player)
   
    def creer_table(self, players):
        """lance un thread table avec les joueurs en entree"""
        new_table=Table(players, self.sb, self.bb)  # qui contient les players de compteur à compteur + i (cf )
        for player in new_table.players:
                player.table=new_table
        self.tables.append(new_table)
        ft.init_client_table(new_table)
        self.thread_table[str(new_table)]=threading.Thread(None, gerer_table, None, [new_table], {})
        self.thread_table[str(new_table)].start()

    def del_table(self, table): 
        #self.tables.remove(table)
        table.end=True
        #del table

    def del_player(self, player):
        #del_thread(self.thread_client[ str(player.connexion) ])
        #del self.thread_client[ str(player.connexion) ]
        player.connexion.close()
        #del player


    #*************** FONCTIONS DE REEQUILIBRAGE DES TABLES ***************************
    def reequilibrage(self):
        """reéquilibrage des tables du tournoi"""
        print("reequilibrage")
        table_min, table_max=give_table_min_max(self.tables)
        repartit_tables=[len(table) for table in self.tables]
        if len(table_max) - len(table_min) >= self.gap_max: 
            self.transfert_player()
        elif give_chaises_dispo(repartit_tables, self.n_max) - self.n_max >=0: 
            # ie on peut répartir les players d'une des tables sur toutes les autres tables, "étape de redistribution"
            table_min.redistribution=True
            print("redistribution de ", table_min, "au prochain tour")

    def redistribution(self, r_table):
        """redistribution des players d'une table vers les autres tables du tournoi"""
        while not self.let_modif_thread:   # ainsi 2 threads ne peuvent pas faire tourner cette fonction en meme temps
            time.sleep(1)                   # et donc ne se gènent pas lors des modifications des tables
        self.let_modif_thread=False
        r_table.in_change=True
        k=len(r_table)
        self.tables.remove(r_table)
        self.tables.sort(key=lambda table: len(table))
        k=0
        n=len(self.tables)
        #on ajoute un player à chaque table de la plus petite à la plus grande et puis on recommence
        while r_table.players:  
            player=r_table.players.pop(0)
            self.tables[k].wait_in.append(player) # on ajoute le player à la liste d'attente de la table
            k= (k+1) % n 
            #ainsi on boucle sur la liste des tables du salon ie quand k==n alors on repart à k==0
        r_table.end=True #supprime la table
        r_table.in_change=False
        self.let_modif_thread=True
    
    #la plus grosse table envoie un player à la plus petite
    #on attend tmax est fini le tour pour lui retirer un player et l'envoyer sur tbale_min
    #pendant ce temps la table_min attend
    def transfert_player(self): 
        """transfert un player de la table la plus grande vers la plus petite"""
        print("transfert")
        table_min, table_max=give_table_min_max(self.tables)

        while table_max.in_change:
            time.sleep(0.01)
        if table_max.wait_in:
            playerchanger=table_max.wait_in.pop(0)  
        else:
            playerchanger = table_max.players[ randint( 0, len(table_max.players)-1 ) ] #embettant car la vrai taille est table.taille
            # et si ils sont tous discnt? ==> impossible grace au while table.in_change qui assure la suppresion des players disconnected dans table
        
        while table_max.in_game:
            time.sleep(3)
        table_max.in_change=True
        #player_à_changer.connexion.send("Vous allez changer de table, patientez un instant".encode()) #mettre un trysend
        table_max.wait_out.append(playerchanger)
        table_min.wait_in.append(playerchanger)
        table_max.in_change=False

    #si il y a de la place dans une table, on ajoute le player à la table
#sinon on ajoute un player d'une table remplie dans la table ou il n'y a plus qu'un player
#comme il y a équilibre à toute étape, ce dernier cas n'est possible que si n_max=3 et table_min=1
#alors on se retrouve avec 2 tables de 2 players et le reste de 3 players, il y a équilibre
    def gerer_player_seul(self, table, player_seul): # si + de 2 tables
        print("gerer_player_seul")
        chaise_dispo=[ (True if len(table) < self.n_max else False) for table in self.tables]
        if sum(chaise_dispo) == 1: #s'il n'y a que la table avec 1 player dedans  #ie il n'existe pas de table avec une place de libre
        #on effectue un transfert de la table_max à la table_min, ie d'une table remplie à une table ou il n'y a plus qu'un player
        #on peut mq que ce cas est unique si self.n_max > 2 et il correspond à 1/3/3/.../3 et qui devient 2/2/3/.../3
            self.transfert_player()

        else: # on insere le player dans la table qui a une place dispo et on détruit la 1ere table 
            #self.del_table(table)
            self.tables.remove(table)
            table.end=True
            table_min=give_table_min_max(self.tables)[0]
            table_min.wait_in.append(player_seul)
