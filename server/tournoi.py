# -*- coding: utf-8 -*-
import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import repartion_joueurs_sur_tables, supprimer_thread, gerer_table, try_recv, wait_for_table, give_table_min_max
from table import Table
from player import Player
from salon import Salon

#TODO: gerer une deconnexion de force d'un client
        

class Tournoi(Salon): #self.n_max est le nombre maximal de joueur par table
    
    def __init__(self, serveur, n_max, stack, small_blind, big_blind, nbr_bot):
        Salon.__init__(self, serveur, n_max, stack, small_blind, big_blind, nbr_bot)
        

    def lancer_tournoi(self):
        self.connexion_des_joueurs()
        self.started=True
        repartion=repartion_joueurs_sur_tables(len(self.players), self.n_max)
        self.remplir_tables(repartion)

   
    def ready(self):
        coefficient=0.7
        return True if sum([joueur.ready for joueur in self.players]) >= coefficient*len(self.players) and len(self.players) >= 2 else False

    def remplir_tables(self, repartition_):
        """lorsque les joueurs sont prets, on les répartit sur les tables de façon équilibrée"""
        marqueur=0
        for taille_table in repartition_:
            self.creer_table(self.players[marqueur : marqueur+taille_table])
            marqueur+=taille_table

    def vainqueur(self, winner):
        #fin du tournoi
        print(winner.name, "a gagné")
        #stop le thread
        pass

    def gerer_deconnexion(self, player_out):
        """réorganisaion des tables lorsqu'un joueur se deconnecte"""
        player_out.disco=True
        self.ask_thread()
        if self.started: 
            table=player_out.table
            table.wait_out.append(player_out)
            if len(self.tables) > 1 and len(table)>1: # s'il n'y a qu'une table et qu'un joueur pas de transfert, ces cas la sont gérés dans la table
                self.reequilibrage()
        else:
            self.supprimer_joueur(player_out) 
        self.let_modif_thread=True
            #si le tournoi n'a pas commencé alors le joueur deconnecté de force
            # n'a aucune conséquence sur les tables, puisqu'elles n'ont pas encore été créée
    
    

    



            
