# -*- coding: utf-8 -*-
import json
import time


def try_recv(player):
    """attend que le client envoie qqchose, si le client est deconnecté ==> execption"""
    client = player.connexion
    salon = player.salon
    if not player.disco:
        try:
            msg = client.recv(1024).decode("utf-8")
            return msg
        except:  # player deconnecté de force
            if not player.disco:
                salon.gerer_deconnexion(player)
            return 'f'


def try_send(player, message):
    """envoie au client le message, si le client est deconnecté ==> execption"""
    client = player.connexion
    salon = player.salon
    if not player.disco:
        try:
            message_json = json.dumps(message).encode("utf-8")
            client.send(message_json)
        except:  # player deconnecté de force
            if not player.disco:
                salon.gerer_deconnexion(player)


# ******LES REFRESH: sont des fonctions qui envoient aux clients les nouvelles infos de la table *****
def refresh_new_game(table, sb_player, bb_player):
    time.sleep(0.3)
    for player in table:
        if not player.bot:
            info_round = {"flag": "new_game",
                          "dealer_id": table.dealer.id,
                          "client_cards": [(player.hand[0].value, player.hand[0].suit),
                                           (player.hand[1].value, player.hand[1].suit)],
                          "blinds": [{"player_id": sb_player.id,
                                      "player_stack": sb_player.stack,
                                      "on_going_bet": sb_player.on_going_bet},
                                     {"player_id": bb_player.id,
                                      "player_stack": bb_player.stack,
                                      "on_going_bet": bb_player.on_going_bet}
                                     ],
                          "speaker_id": table.speaker.id
                          }
            try_send(player, info_round)
        time.sleep(0.3)


def refresh_update(table):  # l'envoie des cartes des players à la fin manquent
    time.sleep(0.3)
    for player in table:
        if not player.bot:
            info_table = {"flag": "update_table",
                          "infos_players": [{"player_id": gamer.id,
                                             "player_stack": gamer.stack,
                                             "on_going_bet": gamer.on_going_bet,
                                             "is_folded": gamer.is_folded,
                                             "is_all_in": gamer.is_all_in} for gamer in table.players],
                          "pot": table.give_pot_total(),
                          "table_cards": [(carte.value, carte.suit) for carte in table.cards],
                          "speaker_id": table.speaker.id
                          }

            try_send(player, info_table)
    time.sleep(0.3)


def refresh_end_game(table):
    time.sleep(0.3)
    players_cards = []
    if table.folded_players() == len(table.players) - 1:  # il ne reste qu'une personne ==> on ne montre pas les cartes
        show_cards = False
    else:
        show_cards = True
        for player in table.players:
            if not player.is_folded:
                players_cards.append((player.id, (
                (player.hand[0].value, player.hand[0].suit), (player.hand[1].value, player.hand[1].suit))))
    for player in table:
        if not player.bot:
            info_winners = {"flag": "end_game",
                            "winners_id": [winner.id for winner in table.final_winners],
                            "show_cards": show_cards,
                            "cards": players_cards
                            }

            try_send(player, info_winners)
    time.sleep(0.3)


# *****************FONCTIONS SALON *************************
def gerer_table(table):
    while not table.end:
        table.set_up_game()
    return


def give_chaises_dispo(repartition_des_tables,
                       reference):  # repartition_des_tables est une liste contenant   le nbr de players par table
    """renvoie les places libres des tables du tournoi"""
    chaises_dispo = 0
    for taille_table in repartition_des_tables:
        chaises_dispo += abs(taille_table - reference)
    return chaises_dispo


def divide_players_on_tables(nbr_players, n_max):
    """renvoie un tableau = repartition équilibrée des players: si 15 players et n_max=4, renvoie: [4,4,4,3]"""
    nbr_tables = nbr_players // n_max
    table_min = nbr_players % n_max
    repartition_tables = [n_max] * nbr_tables
    if table_min != 0:
        repartition_tables += [table_min]
        nbr_tables += 1

    # interresant car recursif  ==> à présenter devant le jury
    nbr_players_mal_repartis = give_chaises_dispo(repartition_tables, min(repartition_tables))
    while nbr_players_mal_repartis >= nbr_tables:
        id_table_min = repartition_tables.index(min(repartition_tables))
        id_table_max = repartition_tables.index(max(repartition_tables))
        repartition_tables[id_table_min] += 1
        repartition_tables[id_table_max] -= 1
        nbr_players_mal_repartis = give_chaises_dispo(repartition_tables, min(repartition_tables))

    return repartition_tables


def del_thread(thread):
    thread.exit()


def wait_for_table(table1, table2):
    """met en pause 2 tables à la fin de leur partie pour d'éventuels modifications"""
    boucle = [table1, table2]
    actuel = True
    while boucle[actuel].in_game:
        actuel = not actuel
        time.sleep(3)
    boucle[actuel].in_change = True
    actuel = not actuel
    while boucle[actuel].in_game:
        time.sleep(3)
    boucle[actuel].in_change = True


def give_table_min_max(list_tables):
    """renvoie la plus petite table et la plus grande selon le nbr de player"""
    list_tables.sort(key=lambda table: len(table))
    table_min = list_tables[0]
    table_max = list_tables[-1]
    return table_min, table_max
