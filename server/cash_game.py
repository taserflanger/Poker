# -*- coding: utf-8 -*-
import time
import threading
from player import Player
from table import Table 
import select
from salon import Salon
from fonction_serveur import give_table_min_max, give_chaises_dispo

class Cash_game(Salon):  #à  faire

    def __init__(self, serveur, n_max, stack, small_blind, big_blind, fichier_data):
        Salon.__init__(self, serveur, n_max, stack, small_blind, big_blind)
        self.gap_max=3

    
    def search_data(self):
        pass
        #avec panda

    def gerer_deconnexion(self, player_out):
        player_out.deco=True
        self.ask_thread()
        #uniquement si le joueur est dans une table
        if player_out is in self.players:
            if player_out.table is not None:
                table=player_out.table
                table.wait_out.append(player_out)
            elif player_out is in self.wait_file:
                self.wait_file.remove(player_out)
            else:
                print("error")
        else:   
            #le joueur n'a pas encore mis son nom
            self.supprimer_joueur(player_out)
        self.let_modif_thread=True

    def launch(self):
        self.ask_thread()
        self.minute_check()
        self.let_modif_thread=True

    def minute_check(self, timeout=60): 
        """créer une nouvelle table si assez de nouveaux joueurs"""
        repartit_tables=[len(table) for table in self.tables]
        current_wait_file=self.wait_file[:]  #empeche les actualisations qui ferait tout bugger
        while len(current_wait_file) > give_chaises_dispo(repartit_tables, self.n_max):
            self.creer_table(current_wait_file[:self.n_max])
            for _ in range(self.n_max):
               self.wait_file.pop(0)
            current_wait_file=self.wait_file[:]
        
        """ajoute les joueurs de la file d'attente à la table la plus petite"""
        while current_wait_file:
            table_min=give_table_min_max(self.tables)
            player_in=current_wait_file.pop(0)
            table_min.wait_in.append(player_in)

        """ redistribution + transfert si len(table_min) - len(table max) >=3 """
        if len(self.tables) > 1:
            self.remaniement()

        """ajout: si une table avec 3joueurs et n_max=3, et 1 joueur en wait_file
         ==> ouverture d'une nouvelle table pour faire T1: 2 joueurs et T2 aussi """

        #relance pas sur que l'on garde ça à l'interieur
        #time.sleep(timeout)
        #self.minute_check()

    #redefinir gerer_joueur_seul
    def gerer_joueur_seul(self, joueur_seul):

        self.wait_file.append(joueur_seul)
        

        

    