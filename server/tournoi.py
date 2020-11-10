import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import ready, repartion_joueurs_sur_tables, supprimer_thread
from table import Table
from player import Player
from salon import Salon

#TODO: gerer une deconnexion de force d'un client
        
def gerer_table(table):
    table.game()
        
class Tournoi(Salon): #self.n_max est le nombre maximal de joueur par table
    
    def __init__(self, serveur, n_max, stack, small_blind, big_blind):
        Salon.__init__(self, serveur, n_max, stack, small_blind, big_blind)


    def lancer_tournoi(self):
        self.connexion_des_joueurs()
        repartion=repartion_joueurs_sur_tables(len(self.players), self.n_max)
        self.remplir_tables(repartion)

   
    def ready(self):
        coefficient=0.7
        return True if sum([joueur.ready for joueur in self.players]) >= coefficient*len(self.players) else False

    def remplir_tables(self, repartition_):
        marqueur=0
        for taille_table in repartition_:
            self.créer_table(self.players[marqueur : marqueur+taille_table])
            marqueur+=taille_table

