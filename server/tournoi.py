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
        marqueur=0
        for taille_table in repartition_:
            nouvelle_table=Table(self.players[marqueur : marqueur+taille_table], self.sb, self.bb)  # qui contient les joueurs de marqueurs à marqueurs + i
            marqueur+=taille_table
            self.tables.append(nouvelle_table)

    def lancer_tournoi(self):
        self.connexion_des_joueurs()
        repartion=repartion_joueurs_sur_tables(len(self.players), self.n_max)
        self.remplir_tables(repartion)
        for table in self.tables:
            self.thread_table[str(table)]=threading.Thread(None, gerer_table, None, (table), {})
            self.thread_table[str(table)].start()
    
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
   

    def deconnexion(self): #il faut que j'ajoute que deconnexion attende que table min et table max ait fini leur tour
        if len(self.tables)>1:
            table_max=self.tables.index( max(self.tables) )
            table_min=self.tables.index( min(self.tables) ) #qui est la table dans laquelle qqun s'est déconnecté
            joueur_changé = []

            for old_table in [table_max, table_min]:
                #suppression des anciens threads
                supprimer_thread(self.thread_table[str(old_table)])
                del self.thread_table[str(old_table)]

                #redifinission des tables suite à la deconnexion d'un joueur
                joueur_à_changer = table_max.players.pop( randint( 0, len(table_max.players) ) )
                new_table= Table(old_table.players + [joueur_changé], self.sb, self.bb)
                joueur_changé=joueur_à_changer
                self.tables.pop( self.tables.index(old_table))
                self.tables.append(new_table) 

                #ajout des nouveaux threads
                self.thread_table[str(new_table)]=threading.Thread(None, gerer_table, None, (new_table), {})
                self.thread_table[str(new_table)].start()
                
          