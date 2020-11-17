import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import repartion_joueurs_sur_tables, supprimer_thread, gerer_table, try_recv, try_send, wait_for_table, give_table_min_max, determiner_joueurs_mal_repartis
from table import Table
from player import Player
from salon import Salon

#TODO: gerer une deconnexion de force d'un client
        

class Tournoi(Salon): #self.n_max est le nombre maximal de joueur par table
    
    def __init__(self, serveur, n_max, stack, small_blind, big_blind):
        Salon.__init__(self, serveur, n_max, stack, small_blind, big_blind)
        

    def lancer_tournoi(self):
        self.connexion_des_joueurs()
        self.started=True
        repartion=repartion_joueurs_sur_tables(len(self.players), self.n_max)
        self.remplir_tables(repartion)

   
    def ready(self):
        coefficient=0.7
        return True if sum([joueur.ready for joueur in self.players]) >= coefficient*len(self.players) and len(self.players) >= 2 else False

    def remplir_tables(self, repartition_):
        marqueur=0
        for taille_table in repartition_:
            self.créer_table(self.players[marqueur : marqueur+taille_table])
            marqueur+=taille_table

    def vainqueur(self, winner):
        #fin du tournoi
        print(winner, "a gagné")
        #stop le thread
        pass

    def gerer_deconnexion(self, joueur_sortant):
        joueur_sortant.disconct=True

        while not self.let_modif_thread:   # ainsi 2 threads ne peuvent pas faire tourner cette fonction en meme temps
            time.sleep(1)                   # et donc ne se gènent pas lors des modifications des tables
        
        self.let_modif_thread=False
        if self.started: 
            table=joueur_sortant.table
            table.ply_disconct.append(joueur_sortant)
            if len(self.tables) == 1: # s'il n'y a qu'une table pas de transfert
                print("table unique")
                print(table.ply_disconct, table.players)
                self.gerer_table_unique(joueur_sortant)

            else:
                if len(table) ==1:
                    self.gerer_joueur_seul(table, joueur_sortant)
                else:
                    self.remaniement(joueur_sortant)
        else:
            self.supprimer_joueur(joueur_sortant) 
        self.let_modif_thread=True
            #si le tournoi n'a pas commencé alors le joueur deconnecté de force
            # n'a aucune conséquence sur les tables, puisqu'elles n'ont pas encore été créée
    
    def gerer_table_unique(self, joueur_sortant):
        table=self.tables[0]
        if len(table)<=1:
            print("fin jeu")
            table.players.remove(joueur_sortant)
            self.vainqueur(table.players[0])


    def remaniement(self, joueur):
        table_min, table_max=give_table_min_max(self.tables)
        repartit_tables=[len(table) for table in self.tables]
        if len(table_max) - len(table_min) >=2: # ne peut être en réalité que ==2 et non >
            self.transfert_joueur()
        elif determiner_joueurs_mal_repartis(repartit_tables, self.n_max) - self.n_max >=0: 
            # ie on peut répartir les joueurs d'une des tables sur toutes les autres tables, "étape de redistribution"
            self.redistribution(table_min)

    def redistribution(self, r_table):
        while r_table.in_game:
            time.sleep(3)
        r_table.in_change=True
        k=len(r_table)
        self.tables.remove(r_table)
        self.tables.sort(key=lambda table: len(table))
        k=0
        n=len(self.tables)
        #on ajoute un joueur à chaque table de la plus petite à la plus grande et puis on recommence
        r_table.manage_file()
        while r_table.players:  
            joueur=r_table.players.pop(0)
            self.tables[k].waiting.append(joueur) # on ajoute le joueur à la liste d'attente de la table
            k= (k+1) % n 
            #ainsi on boucle sur la liste des tables du salon ie quand k==n alors on repart à k==0
        r_table.end=True #supprime la table

    #la plus grosse table envoie un joueur à la plus petite
    #on attend tmax est fini le tour pour lui retirer un joueur et l'envoyer sur tbale_min
    #pendant ce temps la table_min attend
    def transfert_joueur(self): 
        table_min, table_max=give_table_min_max(self.tables)

        while table_max.in_change:
            time.sleep(0.01)
        if table_max.waiting:
            joueur_à_changer=table_max.waiting.pop(0)  
        else:
            joueur_à_changer = table_max.players[ randint( 0, len(table_max.players) ) ] #embettant car la vrai taille est table.taille
            # et si ils sont tous discnt? ==> impossible grace au while table.in_change qui assure la suppresion des joueurs disconnected dans table
        
        while table_max.in_game:
            time.sleep(3)
        table_max.in_change=True
        #joueur_à_changer.connexion.send("Vous allez changer de table, patientez un instant".encode()) #mettre un trysend
        table_max.ply_disconct.append(joueur_à_changer)
        table_min.waiting.append(joueur_à_changer)
        table_max.in_change=False


#si il y a de la place dans une table, on ajoute le joueur à la table
#sinon on ajoute un joueur d'une table remplie dans la table ou il n'y a plus qu'un joueur
#comme il y a équilibre à toute étape, ce dernier cas n'est possible que si n_max=3 et table_min=1
#alors on se retrouve avec 2 tables de 2 joueurs et le reste de 3 joueurs, il y a équilibre
    def gerer_joueur_seul(self, table, joueur): # si + de 2 tables
        chaise_dispo=[ (True if len(table) < self.n_max else False) for table in self.tables]
        if sum(chaise_dispo) == 1: #s'il n'y a que la table avec 1 joueur dedans  #ie il n'existe pas de table avec une place de libre
        #on effectue un transfert de la table_max à la table_min, ie d'une table remplie à une table ou il n'y a plus qu'un joueur
        #on peut mq que ce cas est unique si self.n_max > 2 et il correspond à 1/3/3/.../3 et qui devient 2/2/3/.../3
            self.transfert_joueur()

        else: # on insere le joueur dans la table qui a une place dispo et on détruit la 1ere table 
            joueur.table.players.remove(joueur)
            joueur_seul=table.players[0]
            #self.supprimer_table(table)
            self.tables.remove(table)
            table_min, t=give_table_min_max(self.tables)
            table_min.waiting.append(joueur_seul)
