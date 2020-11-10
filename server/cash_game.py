from fonctions_serveur import demander_reequilibrage
import time
class Cash_game:  #à  faire

    def __init__(self, n_max, small_blind, big_blind):
        self.tables=[]
        self.wait_file=[]
        self.n_max=n_max
        self.sb=small_blind
        self.bb=big_blind

    def creer_table(self, joueurs):
        pass

    def minute_check(self):
        #+ 3 j en liste d'attente
        if len(self.wait_file) >= 3:
            if len(self.wait_file) >=self.n_max:
                self.creer_table(self.wait_file[:self.n_max]) # il peut y avoir trop de joueur dans la liste d'attente ==> créer plusieurs tables
                del self.wait_file[:self.n_max] # ne marche pas ?
            else:
                self.creer_table(self.wait_file)
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
        time.sleep(60)
        self.minute_check()

        

    