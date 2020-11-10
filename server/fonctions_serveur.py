import json
import threading
def initialiser_actualisation(table, small_blind, big_blind):
    for joueur in table:
        client=joueur.connexion
        information_table={"dealer": table.dealer, 
                           "id joueur" : [gamer.id for gamer in table],
                           "cartes" : joueur.hand,
                           "small and big blinds": [small_blind, big_blind]
                           }
        information_table_encodé=json.dumps(information_table)
        client.send(information_table_encodé)
        
def actualiser(table): # il manque l'envoie des cartes du flop etc. ainsi que l'envoie des cartes des joueurs à la fin
    for joueur in table:
        client=joueur.connexion
        information_table={"stacks": [gamer.stack for gamer in table.players], 
                           "on going bet" : [gamer.on_going_bet for gamer in table.players],
                           "folded" : [gamer.is_folded for gamer in table.players],
                           "all in" : [gamer.is_all_in for gamer in table.players],
                           "pots" : table.pots,
                           "cartes table": table.cards
                           }
        information_table_encodé=json.dumps(information_table)
        client.send(information_table_encodé)
        #utiliser info_dictionnaire=json.loads(message)   pour retranscrir en dict

    if table.final_hand:
        for joueur in table:
            client=joueur.connexion
            information_fin_tour= {"cartes" : [(joueur.hand if joueur.final_hand else None) for joueur in table.players], 
                                   "gagnants" : table.final_winners                          
                }
            information_fin_tour_encodé=json.dumps(information_fin_tour)
            client.send(information_fin_tour_encodé)
                        
                      



                  



#**********************************************************************



def ready(players):
    coefficient=0.7

    return True if sum([joueur.ready for joueur in players]) >= coefficient*len(players) else False

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
    thread.raise_execption()
    thread.join()


def remaniement(joueur): # si cette fonction est appelée c'est qu'un joueur s'est déconnecté
    tournoi=joueur.tournoi
    repartit_tables=[len(table.players) for table in tournoi.tables]
    nbr_j_mal_repartis=determiner_joueurs_mal_repartis(repartit_tables)

    joueur.table.players.remove(joueur)
    if nbr_j_mal_repartis >= len(tournoi.tables) and len(tournoi.tables)>=2: 
        tournoi.changement_table()
    else: #création d'une nouvelle table sans le joueur déconnecté 
        old_table=joueur.table
        tournoi.supprimer_joueur(joueur)
        tournoi.créer_table(old_table.players)
        tournoi.supprimer_table(old_table)


        #supprimer joueur et créer une nouvelle table

