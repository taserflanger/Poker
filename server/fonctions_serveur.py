import json
import threading
import itertools
import time
from random import randint


def try_recv(joueur):
    client=joueur.connexion
    salon=joueur.salon
    if not joueur.disco:
        try:
            msg_reçu=client.recv(1024).decode("utf-8")
            return msg_reçu
        except: # joueur deconnecté de force
            salon.gerer_deconnexion(joueur)
            return 'f'


def try_send(joueur, message):
    client=joueur.connexion
    salon=joueur.salon
    if not joueur.disco:
        try:
            client.send(message)
        except: # joueur deconnecté de force
            salon.gerer_deconnexion(joueur)

#utiliser info_dictionnaire=json.loads(message)   pour retranscrir en dict
def initialiser_actualisation(table, small_blind, big_blind):
    for joueur in table:
        try_send(joueur,"actualisation debut".encode("utf-8"))
        info_round={"nom joueurs" : str([player.name for player in table.players]),
                           "dealer": table.dealer.name,
                           "cartes" : str(joueur.hand[0]) + "/" + str(joueur.hand[1]),
                           "small and big blinds": str([small_blind, big_blind])
                           }
        info_round_json=json.dumps(info_round).encode("utf-8")
        time.sleep(0.1)
        try_send(joueur, info_round_json)
    time.sleep(0.1)

def actualiser(table): # l'envoie des cartes des joueurs à la fin manquent
    for joueur in table:
        try_send(joueur, "actualisation tour".encode("utf-8"))
        info_table={"stacks": str([gamer.stack for gamer in table.players]), 
                           "on going bet" : str([gamer.on_going_bet for gamer in table.players]),
                           "folded" : str([gamer.is_folded for gamer in table.players]),
                           "all in" : str([gamer.is_all_in for gamer in table.players]),
                           "pots" : str( [pot[0] for pot in table.pots]),
                           "cartes table": str( [str(carte) for carte in table.cards ])
                           }
        info_table_json=json.dumps(info_table)
        time.sleep(0.1)
        try_send(joueur, info_table_json.encode("utf-8"))

    if table.final_hand:
        for joueur in table:
            try_send(joueur, "actualisation fin".encode("utf-8"))
            info_winners= {"gagnants" : str([gagnant.name for gagnant in table.final_winners])}
            #{"cartes gagnants" : str([ (  str(joueur.hand[0]) + "/" + str(joueur.hand[1]) if joueur.final_hand else None) for joueur in table.players]), 
             #               "gagnants" : str([gagnant.name for gagnant in table.final_winners])}
            info_winners_json=json.dumps(info_winners)
            time.sleep(0.1)
            try_send(joueur, info_winners_json.encode("utf-8"))
    time.sleep(0.1)

        
def gerer_table(table):
    while not table.end:
        table.set_up_game()
    return

def give_chaises_dispo(repartition_des_tables, reference): #repartition_des_tables est une liste contenant    # le nbr de joueurs par table
        nbr_joueurs_mal_repartis=0
        for taille_table in repartition_des_tables:
            nbr_joueurs_mal_repartis += abs(taille_table - reference)
        return nbr_joueurs_mal_repartis
    
def repartion_joueurs_sur_tables(nbr_joueurs, n_max):  
    nbr_tables= nbr_joueurs // n_max
    table_min=nbr_joueurs % n_max  
    repartition_tables=[n_max]*nbr_tables  
    if table_min != 0:
        repartition_tables += [table_min]   
        nbr_tables+=1
    

    #interresant car recursif  ==> à présenter devant le jury
    nbr_joueurs_mal_repartis = give_chaises_dispo(repartition_tables, min (repartition_tables) ) 
    while nbr_joueurs_mal_repartis >= nbr_tables:   
        id_table_min= repartition_tables.index( min (repartition_tables) )
        id_table_max= repartition_tables.index( max (repartition_tables) )
        repartition_tables[id_table_min]+=1
        repartition_tables[id_table_max]-=1
        nbr_joueurs_mal_repartis = give_chaises_dispo(repartition_tables, min(repartition_tables))
 
    return repartition_tables


def supprimer_thread(thread):
    thread.exit()


"""
def demander_reequilibrage(salon):  
    repartit_tables=[len(table.players) for table in salon.tables]
    nbr_j_mal_repartis=give_chaises_dispo(repartit_tables, min(repartit_tables))
    #joueur_seul= True if sum([True if len(salon.players)==1 else False]) else False
    if nbr_j_mal_repartis >= len(salon.tables) and len(salon.tables)>=2:  
        transfert_joueur(salon.tables)


#salon fait reference à tournoi ou cashgame
def remaniement(joueur): # si cette fonction est appelée c'est qu'un joueur s'est déconnecté
    salon=joueur.tournoi
    joueur.table.players.remove(joueur)
    demander_reequilibrage(salon)
    #salon.supprimer_joueur(joueur)
"""


#fonction qui sert à mettre en pause 2 tables sans interrompre leur partie, donc 
#les mettre en pause pendant table.in_game= False
#la premiere qui finit attend l'autre
def wait_for_table(table1, table2): 
    boucle=[table1, table2]
    actuel=True
    while boucle[actuel].in_game:
        actuel= not actuel
        time.sleep(3) 
    boucle[actuel].in_change=True
    actuel=not actuel
    while boucle[actuel].in_game:
        time.sleep(3)
    boucle[actuel].in_change=True

def give_table_min_max(list_tables, booleen=True): #mettre en pause les autres threads pour pas de pblm
    list_tables.sort(key=lambda table: len(table))
    table_min=list_tables[0]
    table_max=list_tables[-1]
    return table_min, table_max if booleen else table_min
        




