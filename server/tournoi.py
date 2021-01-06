# -*- coding: utf-8 -*-
import socket
import threading
import select
import time
import json
from random import randint
from fonctions_serveur import divide_players_on_tables, del_thread, gerer_table, try_recv, wait_for_table
from table import Table
from player import Player
from salon import Salon

#TODO: gerer une deconnexion de force d'un client
        

class Tournoi(Salon): #self.n_max est le nombre maximal de player par table
    
    def __init__(self, serveur, n_max, stack, small_blind, big_blind, nbr_bot):
        Salon.__init__(self, serveur, n_max, stack, small_blind, big_blind, nbr_bot)
        

    def lancer_tournoi(self):
        self.players_connexion()
        self.started=True
        repartion=divide_players_on_tables(len(self.players), self.n_max)
        self.remplir_tables(repartion)
   
    def ready(self):
        """condition de lancement du tournoi: si 70% des players connectés sont prets"""
        coefficient=0.7
        return True if sum([player.ready for player in self.players]) >= coefficient*len(self.players) and len(self.players) >= 2 else False

    def remplir_tables(self, repartition):
        """lorsque les players sont prets, on les répartit sur les tables de façon équilibrée"""
        compteur=0
        for taille_table in repartition:
            self.creer_table(self.players[compteur : compteur+taille_table])
            compteur+=taille_table

    def gerer_deconnexion(self, player_out):
        """réorganisaion des tables lorsqu'un player se deconnecte"""
        player_out.disco=True
        self.ask_thread()
        if self.started: 
            table=player_out.table
            table.wait_out.append(player_out)
            if len(self.tables) > 1 and len(table)>1: 
                self.reequilibrage()
            # le cas 1 table et 1 player ==> pas de transfert, c'est géré dans table.py\Table
        else:
            self.del_player(player_out) 
        self.let_modif_thread=True
            #si le tournoi n'a pas commencé alors le player est supprimé
    

    
    

    



            
