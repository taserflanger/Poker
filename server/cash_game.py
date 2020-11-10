from fonctions_serveur import demander_reequilibrage
import time
import threading
from player import Player
from table import Table 
import select
from salon import Salon

class Cash_game(Salon):  #à  faire

    def __init__(self, serveur, n_max, stack, small_blind, big_blind):
        Salon.__init__(self, serveur, n_max, stack, small_blind, big_blind)

    def deconnexion(self, joueur):
        table=joueur.table
        self.supprimer_joueur(joueur)
        if len(table.players)==1:
            self.wait_file.insert(0, table.players)
            self.supprimer_table(table)
    

    def minute_check(self, timeout=60):
        #+ 3 j en liste d'attente
        if len(self.wait_file) >= 3:
            if len(self.wait_file) >=self.n_max:
                self.créer_table(self.wait_file[:self.n_max]) # il peut y avoir trop de joueur dans la liste d'attente ==> créer plusieurs tables
                del self.wait_file[:self.n_max] # ne marche pas ?
            else:
                self.créer_table(self.wait_file)
                self.wait_file=[]

        # - de 4 joueurs dans une table        
        for table in self.tables:
            if len(table.players) <= 3:
                demander_reequilibrage(self.tables)
        
        #differce de taille entre 2 tables >=3
        self.tables.sort(key=lambda table: len(table.players))
        table_min=self.tables[0]
        table_max=self.tables[-1]
        if len(table_max.players) - len(table_min.players) >= 3:
            demander_reequilibrage(self.tables)

        
        #fusion entre 2 tables possibles
        ...

        #relance
        time.sleep(timeout)
        self.minute_check()

        

    