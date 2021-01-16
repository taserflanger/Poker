import threading
import time

from .server_utils import give_table_min_max, give_chaises_dispo
from .server_utils import try_send, try_recv
from server import Salon


class CashGame(Salon):  # à  faire

    def __init__(self, serveur, n_max, stack, small_blind, big_blind, nbr_bot, fichier_data):
        Salon.__init__(self, serveur, n_max, stack, small_blind, big_blind, nbr_bot)
        self.gap_max = 3
        self.fichier_data = fichier_data  # est un dataFrame de pandas
        self.end = False

    def write_data(self, name, password):
        self.fichier_data = self.fichier_data.append({"name": name, "stack": str(self.stack), "password": password},
                                                     ignore_index=True)
        self.fichier_data.to_csv("/tmp_data/data.csv", index=False)

    def gerer_deconnexion(self, player_out):
        player_out.deco = True
        self.ask_thread()
        # uniquement si le joueur est dans une table
        if player_out in self.players:
            if player_out.table is not None:
                table = player_out.table
                table.wait_out.append(player_out)
            elif player_out in self.wait_file:
                self.wait_file.remove(player_out)
            else:
                print("error")
        else:
            # le joueur n'a pas encore mis son nom
            self.del_player(player_out)
        self.let_modif_thread = True

    # on peut mettre tout ça coté client
    def sign_in(self, joueur):  # on peut ajouter une confirmation
        try_send(joueur, {"flag": "preparation"})
        name = try_recv(joueur)  # si name=="" c'est que le joueur souhaite créer un nouveau compte
        if name == "''":  # sinon c'est qu'il s'est connecté à son compte
            time.sleep(0.3)
            print("in")
            name = try_recv(joueur)
            while name in self.liste_noms + [""] or name in self.fichier_data["name"].values:
                try_send(joueur, {"flag": "erreur nom"})  # erreur nom correspond à un nom deja pris
                name = try_recv(joueur)
            try_send(joueur, {"flag": "correct_name"})
            password = try_recv(joueur)
            self.write_data(name, password)
        print("out")
        return name

    def launch(self):
        connexion_thread = threading.Thread(None, self.connexion_des_joueurs, None, {})
        connexion_thread.start()
        while not self.end:
            time.sleep(20)
            self.minute_check()

    def minute_check(self):
        for _ in self.wait_file:
            print(_.name, end=" ")
        print("")
        if len(self.players) > 1:  # ajouter une condition pour que les joueurs soit pret
            repartit_tables = [len(table) for table in self.tables]
            current_wait_file = self.wait_file[:]  # empeche les actualisations qui ferait tout bugger

            """remplir les tables qui ont des chaises libres, et ajoute les joueurs à la + petite table"""
            while give_chaises_dispo(repartit_tables, self.n_max) > 0 and current_wait_file:
                print("remplissage")
                table_min, t = give_table_min_max(self.tables)
                player_in = self.wait_file.pop(0)
                current_wait_file = self.wait_file[:]  # permet une actualisation des la liste d'attente
                table_min.wait_in.append(player_in)
                repartit_tables = repartit_tables = [len(table) for table in
                                                     self.tables]  # prend en compte le joueur ajouté

            """créer une nouvelle table si assez de nouveaux joueurs"""
            while len(current_wait_file) > give_chaises_dispo(repartit_tables, self.n_max) and len(
                    current_wait_file) > 1:
                print("creation table")
                n = len(current_wait_file)
                if n > self.n_max:
                    n = self.n_max
                self.creer_table(current_wait_file[:n])
                for _ in range(n):
                    self.wait_file.pop(0)
                current_wait_file = self.wait_file[:]

            """ redistribution + transfert si len(table_min) - len(table max) >=3 """
            if len(self.tables) > 1:
                self.reequilibrage()

            """ajout: si une table avec 3joueurs et n_max=3, et 1 joueur en wait_file
             ==> ouverture d'une nouvelle table pour faire T1: 2 joueurs et T2 aussi """

    # redefinir gerer_joueur_seul
    def gerer_joueur_seul(self, joueur_seul):
        self.wait_file.append(joueur_seul)
