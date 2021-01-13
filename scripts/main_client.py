"""
Correspond au script exécutable du programme client. Utilise tous les 'Widgets' PyQt5 personnalisés de custom_widgets.
Choisir le mode (local ou serveur) avant d'exécuter.
"""
import json
import socket
import sys
from sys import argv

from client.custom_widgets import *

SERVER = "178.79.165.80"
LOCAL = 'localhost'
PORT = 4500
MODE = SERVER
print(argv)
if len(argv) >= 1 and argv[1] == "local":
    MODE = LOCAL
try:
    PORT = int(argv[2])
except (ValueError, IndexError):
    pass


class Server_handler(QObject):
    infos_server = pyqtSignal(str)

    @pyqtSlot()
    def handle_server(self):
        while True:
            msg_server = server.recv(1024).decode()
            self.infos_server.emit(msg_server)


class main_window(QMainWindow):
    start_comm = pyqtSignal()

    def __init__(self, server):

        QMainWindow.__init__(self)
        self.server = server
        self.table = None
        self.init_widget_home()
        self.functions_dict = {'init_table': self.init_table, 'new_game': self.new_game,
                               'update_table': self.update_table, 'end_game': self.end_game, 'action': self.action,
                               'name ok': self.widget_home.ask_if_ready, 'error name': self.widget_home.wrong_name,
                               'disconnect': self.disconnect}

        self.setObjectName("main_window")
        self.setWindowTitle("PSL Poker")
        self.setMinimumSize(QSize(300, 230))

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setGeometry(QRect(0, 0, 900, 22))
        self.menu_bar.setObjectName("menu_bar")

        self.server_handler = Server_handler()
        self.server_handler_thread = QThread()
        self.server_handler.moveToThread(self.server_handler_thread)
        self.server_handler_thread.start()

        self.start_comm.connect(self.server_handler.handle_server)
        self.server_handler.infos_server.connect(self.server_to_functions)

        self.show()
        self.start_comm.emit()

    def init_widget_home(self):

        self.resize(430, 300)
        self.widget_home = widget_home(server=server)
        self.setCentralWidget(self.widget_home)

    def init_widget_game(self):
        self.resize(1000, 700)
        self.client_name = self.widget_home.client_name
        self.setWindowTitle(f"PSL Poker - {self.client_name}")
        self.widget_game = widget_game(server=server)
        self.setCentralWidget(self.widget_game)

    @pyqtSlot(str)
    def server_to_functions(self, msg_server):

        serv_inf = json.loads(msg_server)
        print(f"\nFrom server to client :\n")
        for key, value in serv_inf.items():
            print(f"{key} : {value}")
        self.functions_dict[serv_inf['flag']](serv_inf)

    def init_table(self, serv_inf):
        players, time_to_play = serv_inf['players_data'], 30
        for i in range(len(players)):
            p = players[i]
            players[i] = Player(p['name'], p['id'], p['stack'], p['is_player'])
        self.init_widget_game()
        self.table = Table(players=players, widget_game=self.widget_game, time_to_play=time_to_play)
        self.table.show_used_widgets()
        self.repaint()
        print('Table has been initiated')

    def new_game(self, serv_inf):
        players, table_cards, dealer_id = self.table.players, self.table.widget_table.table_cards, serv_inf['dealer_id']
        client_cards = serv_inf['client_cards']
        sb, bb = serv_inf['blinds']
        for player in players:
            player.widget_player.is_not_speaking_and_did_not_win()
            if player.id == serv_inf['speaker_id']:
                player.widget_player.is_speaking()
            player.is_folded = player.is_all_in = False
            player.set_ogb(0)
            player.show_dealer_button(player.id == dealer_id)
            if player.is_client:
                player.widget_player.p_0_cards.set_cards(card1=client_cards[0], card2=client_cards[1])
            player.show_cards(True)
            for blind in [sb, bb]:
                if player.id == blind['player_id']:
                    player.set_ogb(blind['on_going_bet'])
                    player.set_stack(blind['player_stack'])
        table_cards.new_game()
        print('New_game has been started')

    def update_table(self, serv_inf):
        infos_players = serv_inf['infos_players']
        for infos_player in infos_players:
            player = self.table.get_player_from_id(infos_player['player_id'])
            player.set_ogb(infos_player['on_going_bet'])
            player.set_stack(infos_player['player_stack'])
            if infos_player['is_folded']:
                if not player.is_folded:
                    player.folds()
            if infos_player['is_all_in']:
                if not player.is_all_in:
                    player.all_in()
            if player.id == serv_inf['speaker_id']:
                player.widget_player.is_speaking()
            else:
                player.widget_player.is_not_speaking_and_did_not_win()
        self.table.set_pot(serv_inf['pot'])
        self.table.widget_table.table_cards.set_cards(serv_inf['table_cards'])
        print('Table has been updated')

    def action(self, serv_inf):
        stack, ogb = self.table.client_player.stack, self.table.client_player.ogb
        amount_to_call = serv_inf['amount_to_call']
        self.table.widget_game.action(stack, ogb, amount_to_call)
        print('Action has initiated')

    def end_game(self, serv_inf):
        for player in self.table.players:
            player.widget_player.is_not_speaking_and_did_not_win()
        for winner_id in serv_inf['winners_id']:
            winner = self.table.get_player_from_id(winner_id)
            winner.widget_player.won()
        if serv_inf['show_cards']:
            self.widget_end_game = widget_end_game(serv_inf['cards'])
        self.table.set_pot(0)
        print('Game has ended')

    def disconnect(self, serv_inf):
        print('Player has been disconnected')
        app.quit()

    def resizeEvent(self, e):
        w = self.width()
        self.setFixedHeight(0.7 * w)


class Player:
    def __init__(self, name, id, stack, is_client=False):
        self.name = name
        self.ogb = 0
        self.stack = stack
        self.is_client = is_client
        self.is_folded = self.is_all_in = False
        self.id = id

    def set_attributes(self, widget_p, widget_f):
        self.widget_player = widget_p
        self.widget_front = widget_f
        self.widget_player.label_name.setText(self.name)
        self.set_stack(self.stack)
        if self.is_client:
            self.widget_player.p_0_cards.set_name(self.name)

    def show_dealer_button(self, value):
        if value:
            self.widget_front.label_dealer.show()
        else:
            self.widget_front.label_dealer.hide()

    def show_cards(self, value):
        if value:
            self.widget_player.show_cards()
        else:
            self.widget_player.hide_cards()

    def set_ogb(self, value):
        self.ogb = value
        if value > 0:
            self.widget_front.widget_ogb.label.setText(str(value))
            self.widget_front.widget_ogb.show()
        else:
            self.widget_front.widget_ogb.hide()

    def set_stack(self, value):
        self.stack = value
        self.widget_player.label_stack.setText(str(value))

    def folds(self):
        self.widget_player.hide_cards()
        self.is_folded = True

    def all_in(self):
        self.widget_player.is_all_in()
        self.is_all_in = True


class Table:
    def __init__(self, players, widget_game, time_to_play):
        self.players = players
        self.nb_players = len(self.players)
        self.time_to_play = time_to_play
        self.widget_game, self.widget_table = widget_game, widget_game.widget_table
        for player in self.players:
            if player.is_client:
                self.client_player = player
        self.base_id = self.client_player.id
        self.connect_players_to_widgets()

    def connect_players_to_widgets(self):
        """On donne ici le table_id à chaque joueur de la table, et on donne à chaque joueur ses attributs
        wp et wf (widget_player et widget_front)"""

        ind_client = self.players.index(self.client_player)
        self.players.sort(key=lambda x: x.id)
        self.players = self.players[ind_client:] + self.players[:ind_client]
        for ind in range(self.nb_players):
            self.players[ind].table_id = table_ids_order[ind]
            ordered_widgets = sorted(table_ids_order[:self.nb_players])
            widget_id = ordered_widgets[ind]
            self.players[ind].set_attributes(widget_p=self.widget_table.widget_players[widget_id],
                                             widget_f=self.widget_table.widget_fronts[widget_id])

    def show_used_widgets(self):
        for player in self.players:
            player.widget_front.show()
            player.widget_player.show()

    def get_player_from_id(self, id):
        for player in self.players:
            if player.id == id:
                return player

    def set_pot(self, value):
        if value > 0:
            self.widget_table.table_cards.widget_pot.label.setText(str(value))
            self.widget_table.table_cards.widget_pot.show()
        else:
            self.widget_table.table_cards.widget_pot.hide()


def send_server(dico, server):
    dico = json.dumps(dico)
    print('From client to server : ', dico)
    server.send(dico.encode())


table_ids_order = [0, 4, 3, 2, 5, 1, 6]

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((MODE, PORT))
    app = QApplication(sys.argv)
    game_window = main_window(server)
    sys.exit(app.exec_())

