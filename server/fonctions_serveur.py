import json
import threading

#utiliser info_dictionnaire=json.loads(message)   pour retranscrir en dict
def initialiser_actualisation(table, small_blind, big_blind):
    for joueur in table:
        client=joueur.connexion
        client.send("actualisation debut".encode("utf-8"))
        info_round={"nom joueurs" : str([player.name for player in table.players]),
                           "dealer": table.dealer.name,
                           "cartes" : str(joueur.hand[0]) + "/" + str(joueur.hand[1]),
                           "small and big blinds": str([small_blind, big_blind])
                           }
        info_round_json=json.dumps(info_round).encode("utf-8")
        client.send(info_round_json)

def actualiser(table): # l'envoie des cartes des joueurs à la fin manquent
    for joueur in table:
        client=joueur.connexion
        client.send("actualisation tour".encode("utf-8"))
        info_table={"stacks": str([gamer.stack for gamer in table.players]), 
                           "on going bet" : str([gamer.on_going_bet for gamer in table.players]),
                           "folded" : str([gamer.is_folded for gamer in table.players]),
                           "all in" : str([gamer.is_all_in for gamer in table.players]),
                           "pots" : str(table.pots),
                           "cartes table": str( [str(carte) for carte in table.cards ])
                           }
        info_table_json=json.dumps(info_table)
        client.send(info_table_json.encode("utf-8"))

    if table.final_hand:
        for joueur in table:
            client=joueur.connexion
            client.send("actualisation fin".encode("utf-8"))
            info_winners= {"cartes gagnants" : str([ (  str(joueur.hand[0]) + "/" + str(joueur.hand[1]) if joueur.final_hand else None) for joueur in table.players]), 
                            "gagnants" : str([gagnant.name for gagnant in table.final_winners])}
            info_winners_json=json.dumps(info_winners)
            client.send(info_winners_json.encode("utf-8"))


def determiner_joueurs_mal_repartis(repartition_des_tables): #repartition_des_tables est une liste contenant
        reference= min (repartition_des_tables)              # le nbr de joueurs par table
        nbr_joueurs_mal_repartis=0
        for taille_table in repartition_des_tables:
            nbr_joueurs_mal_repartis += (taille_table - reference)
        return nbr_joueurs_mal_repartis
    
def repartion_joueurs_sur_tables(nbr_joueurs, n_max):  
    nbr_tables= nbr_joueurs // n_max
    table_min=nbr_joueurs % n_max  
    repartition_tables=[n_max]*nbr_tables  
    if table_min != 0:
        repartition_tables += [table_min]   
        nbr_tables+=1
    
    nbr_joueurs_mal_repartis = determiner_joueurs_mal_repartis(repartition_tables) 
    while nbr_joueurs_mal_repartis >= nbr_tables:
        id_table_min= repartition_tables.index( min (repartition_tables) )
        id_table_max= repartition_tables.index( max (repartition_tables) )
        repartition_tables[id_table_min]+=1
        repartition_tables[id_table_max]-=1
        nbr_joueurs_mal_repartis = determiner_joueurs_mal_repartis(repartition_tables)
 
    return repartition_tables


def supprimer_thread(thread):
    thread.raise_exception()
    thread.join()


def demander_reequilibrage(salon):  
    repartit_tables=[len(table.players) for table in salon.tables]
    nbr_j_mal_repartis=determiner_joueurs_mal_repartis(repartit_tables)
    if nbr_j_mal_repartis >= len(salon.tables) and len(salon.tables)>=2: 
        transfert_joueur(salon.tables)


#salon fait reference à tournoi ou cashgame
def remaniement(joueur): # si cette fonction est appelée c'est qu'un joueur s'est déconnecté
    salon=joueur.salon 
    joueur.table.players.remove(joueur)
    demander_reequilibrage(salon)
    salon.supprimer_joueur(joueur)
  

import itertools
import time
from random import randint

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


#la plus grosse table envoie un joueur à la plus petite
def transfert_joueur(liste_tables): 
    liste_tables.sort(key=lambda table: len(table.players))
    table_min=liste_tables[0]
    table_max=liste_tables[-1]
    wait_for_table(table_max, table_min)

    joueur_à_changer = table_max.players.pop( randint( 0, len(table_max.players) ) )
    joueur_à_changer.connexion.send("Vous allez changer de table, patientez un instant".encode())
    table_max.players.remove(joueur_à_changer)
    table_min.players.append(joueur_à_changer)

    table_min.in_change=False
    table_max.in_change=False




