# -*- coding: utf-8 -*-
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
            msg=client.recv(1024).decode("utf-8")
            return msg
        except: # joueur deconnecté de force
            if not joueur.disco:
                salon.gerer_deconnexion(joueur)
            return 'f'


def try_send(joueur, message):
    client=joueur.connexion
    salon=joueur.salon
    if not joueur.disco:
        try:
            message_json=json.dumps(message).encode("utf-8")
            client.send(message_json)
        except: # joueur deconnecté de force
            if not joueur.disco:
                salon.gerer_deconnexion(joueur)
            

#utiliser info_dictionnaire=json.loads(message)   pour retranscrir en dict
def initialiser_actualisation(table, small_blind, big_blind):
    time.sleep(0.3)
    for joueur in table:
        if not joueur.bot:
            info_round={"flag": "new_game",
                        "dealer_id": str(table.dealer.id),
                        "client_cards" : str([(joueur.hand[0].value, joueur.hand[0].suit), (joueur.hand[1].value, joueur.hand[1].suit)]),
                                                       }
            try_send(joueur, info_round)
        time.sleep(0.3)


def actualiser(table): # l'envoie des cartes des joueurs à la fin manquent
    time.sleep(0.3)
    for joueur in table:
        if not joueur.bot:
            info_table={"flag": "update table",
                        "infos_players": str([{"player_id":gamer.id,
                                          "player_stack": gamer.stack, 
                                          "on_going_bet" :gamer.on_going_bet,
                                          "is_folded" : gamer.is_folded,
                                          "is_all_in" : gamer.is_all_in} for gamer in table.players]),
                        "pot" : str(table.give_pot_total()),
                        "table_cards": str([(carte.value, carte.suit) for carte in table.cards ]),
                        "speaker_id": str(table.next_player(table.speaker))
                               }
        
            try_send(joueur, info_table)
    time.sleep(0.3)

def actualsation_finale(table):
    time.sleep(0.3)
    for joueur in table:
        if not joueur.bot:
            players_cards=[]
            if table.folded_players() == len(table.players)-1: #il ne reste qu'une personne ==> on ne montre pas les cartes
                show_cards=False   
            else: 
                show_cards=True
                for player in table.players:
                    if not player.is_folded:
                        players_cards.append( ( player.id, ((player.hand[0].value, player.hand[0].suit), (player.hand[1].value, player.hand[1].suit)) ))
                
            info_winners= { "flag": "end_game",
                            "winners_id" : str([winner.id for winner in table.final_winners]),
                            "show_cards": str(show_cards),
                            "cards": str(players_cards)
                            }
        
            try_send(joueur, info_winners)
    time.sleep(0.3)

        
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
        





