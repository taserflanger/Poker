"""
Regroupe toutes les classes de 'Widgets' PyQt5 personnalisés, exceptée la fenêtre principale écrite dans main_client.
"""

import gui_resources, random
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from main_client import *

class widget_home(QWidget):

    names = ['Rodrigue', 'Pascal', 'Andres', 'Fx', 'Martin', 'Julien', 'Saïdi', 'Michou', 'Zizou', 'Francisco']

    def __init__(self, server=None, test_phase=True):
        QWidget.__init__(self)
        self.server = server
        self.test_phase = test_phase
        self.setObjectName('widget_home')

        self.glayout = QGridLayout(self)
        self.glayout.setObjectName('glayout_home')

        self.label_title = QLabel(self)
        self.label_title.setText('Poker CPES')
        self.label_title.setStyleSheet(" font-size: 34px; ")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.glayout.addWidget(self.label_title, 0, 1, 2, 3)
        self.setSizePolicy(sizePolicy)

        self.line_name = QLineEdit(self)
        self.line_name.setText("Write your name")
        self.line_name.setStyleSheet("font-size: 12px;")
        if test_phase:
            self.line_name.setText(random.choice(self.names))
        self.glayout.addWidget(self.line_name, 2, 1, 1, 3)

        self.label_error = QLabel(self)
        self.label_error.setText('This name is already used.')
        self.label_error.setSizePolicy(sizePolicy)
        self.label_error.setAlignment(Qt.AlignRight)
        self.glayout.addWidget(self.label_error, 3, 1, 1, 3)
        self.label_error.hide()
        self.label_error.setStyleSheet("color: 'red'; font-size: 14px;")

        self.label_ready = QLabel(self)
        self.label_ready.setText('Are you ready to play?')
        self.label_ready.setSizePolicy(sizePolicy)
        self.label_ready.setAlignment(Qt.AlignRight)
        self.label_ready.hide()
        self.label_ready.setStyleSheet("font-size: 14px;")

        self.button_enter = QPushButton(self)
        self.glayout.addWidget(self.button_enter, 4, 2, 1, 2)
        self.button_enter.clicked.connect(self.send_name)
        self.button_enter.setSizePolicy(sizePolicy)
        self.button_enter.setText("Enter")
        self.button_enter.setStyleSheet("font-size: 18px;")

        self.button_ready = QPushButton(self)
        self.button_ready.setSizePolicy(sizePolicy)
        self.button_ready.hide()
        self.button_ready.clicked.connect(self.send_ready)
        self.button_ready.setText("Ready")
        self.button_ready.setEnabled(False)
        self.button_ready.setStyleSheet("font-size: 18px;")

        self.widget_spacer = QWidget(self)
        self.glayout.addWidget(self.widget_spacer, 5, 0, 1, 1)

        for i, hs in (0, 1), (1, 1), (2, 1), (3, 1), (4, 1):
            self.glayout.setColumnStretch(i, hs)

        for i, vs in (0, 5), (1, 5), (2, 20), (3, 5), (4, 1), (5, 5):
            self.glayout.setRowStretch(i, hs)

    @pyqtSlot()
    def send_name(self):
        self.client_name = self.line_name.text()
        send_server({'flag': 'name', 'name': self.client_name}, self.server)

    @pyqtSlot()
    def send_ready(self):
        self.button_ready.setEnabled(False)
        self.setEnabled(False)
        send_server({'flag': 'ready'}, self.server)

    def wrong_name(self, serv_inf):
        self.label_error.show()
        if self.test_phase:
            self.line_name.setText(random.choice(self.names))

    def ask_if_ready(self, serv_inf):
        self.line_name.setEnabled(False)
        self.glayout.replaceWidget(self.button_enter, self.button_ready)
        self.button_ready.show()
        self.button_ready.setEnabled(True)
        self.button_enter.setEnabled(False)
        self.button_enter.hide()

        self.glayout.replaceWidget(self.label_error, self.label_ready)
        self.label_error.hide()
        self.label_ready.show()


class widget_empty(QWidget):

    def __init__(self, parent=None, name="widget_empty", hstretch=0, vstretch=0, msize=(0, 0),
                 Msize=(100000, 100000)):

        QWidget.__init__(self, parent)
        self.setObjectName(name)

        sizePolicy2 = sizePolicy
        sizePolicy2.setHorizontalStretch(hstretch)
        sizePolicy2.setVerticalStretch(vstretch)
        self.setSizePolicy(sizePolicy2)
        self.setMaximumHeight(Msize[1])
        self.setMaximumWidth(Msize[0])
        self.setMinimumHeight(msize[1])
        self.setMinimumWidth(msize[0])


class widget_cards_player(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        self.setWindowTitle(f"Cards")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.setGeometry(QRect(100, 290, 251, 191))
        self.setObjectName("widget_cards_player")

        self.hlayout = QHBoxLayout(self)
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.setObjectName("hlayout")

        self.p0_card_1 = QLabel(self)
        self.p0_card_1.setSizePolicy(sizePolicy)
        self.p0_card_1.setPixmap(QPixmap(":/imgs/imgs/cards_imgs/14_0.png"))
        self.p0_card_1.setScaledContents(True)
        self.p0_card_1.setObjectName("p0_card_1")
        self.p0_card_1.setMinimumSize(50, 50)
        self.hlayout.addWidget(self.p0_card_1)

        self.p0_card_2 = QLabel(self)
        self.p0_card_2.setSizePolicy(sizePolicy)
        self.p0_card_2.setPixmap(QPixmap(":/imgs/imgs/cards_imgs/14_0.png"))
        self.p0_card_2.setScaledContents(True)
        self.p0_card_2.setObjectName("p0_card_2")
        self.p0_card_2.setMinimumSize(50, 50)
        self.hlayout.addWidget(self.p0_card_2)

        self.hide()

    def set_cards(self, card1, card2):
        self.p0_card_1.setPixmap(QPixmap(card_img(card1)))
        self.p0_card_2.setPixmap(QPixmap(card_img(card2)))
        self.show()

    def set_name(self, name):
        self.setWindowTitle(f"Cards - {name}")


class widget_end_game(QWidget):

    def __init__(self, cards_inf):

        QWidget.__init__(self)
        self.setWindowTitle("Cards - End of the game")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.glayout = QGridLayout(self)
        n = len(cards_inf)
        self.names = [None] * 5
        self.cards = [None] * 5
        for ind in range(n):
            player_name, card1, card2 = cards_inf[ind][0], cards_inf[ind][1][0], cards_inf[ind][1][1]
            self.names[ind] = (QLabel(self))
            self.names[ind].setText(player_name)
            self.cards[ind] = widget_cards_player(self)
            self.cards[ind].set_cards(card1, card2)
            self.glayout.addWidget(self.names[ind], ind, 0, 1, 1)
            self.glayout.addWidget(self.cards[ind], ind, 1, 1, 1)
        self.resize(75, n * 35)
        self.show()


class widget_player(QWidget):

    def __init__(self, parent=None, name="widget_player", empty=False, p_0=False):

        QWidget.__init__(self, parent)
        self.setObjectName("widget_player")
        self.p_0 = p_0

        self.setSizePolicy(sizePolicy)

        self.glayout_wp = QGridLayout(self)
        self.glayout_wp.setContentsMargins(0, 0, 0, 0)
        self.glayout_wp.setVerticalSpacing(0)
        self.glayout_wp.setObjectName("glayout_wp")

        self.pix_cards = QLabel(self)
        self.pix_cards.setSizePolicy(sizePolicy)
        self.pix_cards.setMinimumSize(QSize(0, 0))
        self.pix_cards.setMaximumSize(QSize(10000, 10000))

        self.half_cards = QPixmap(":/imgs/imgs/half_cards.png")
        self.half_cards_purple = QPixmap(':/imgs/imgs/half_cards_purple.png')
        self.half_cards_blue = QPixmap(':/imgs/imgs/half_cards_blue.png')
        self.half_cards_red = QPixmap(':/imgs/imgs/half_cards_red.png')
        self.half_cards_yellow = QPixmap(':/imgs/imgs/half_cards_yellow.png')

        self.actual_cards = self.half_cards

        self.pix_cards.setPixmap(self.actual_cards)
        self.pix_cards.setScaledContents(False)
        self.pix_cards.setAlignment(Qt.AlignHCenter)
        self.pix_cards.setAlignment(Qt.AlignBottom)
        self.pix_cards.setObjectName("pix_cards")
        self.glayout_wp.addWidget(self.pix_cards, 0, 0, 1, 1)
        self.pix_cards.hide()

        self.label_name = QLabel(self)
        self.label_name.setMinimumSize(QSize(0, 0))
        self.label_name.setMaximumSize(QSize(10000, 10000))
        self.label_name.setStyleSheet("image: url(:/imgs/imgs/label_bg.png);color: 'white'")
        self.label_name.setAlignment(Qt.AlignCenter)
        self.label_name.setObjectName("label_name")
        self.label_name.setText("Name")
        self.glayout_wp.addWidget(self.label_name, 1, 0, 1, 1)

        self.label_stack = QLabel(self)
        self.label_stack.setMinimumSize(QSize(0, 0))
        self.label_stack.setMaximumSize(QSize(10000, 10000))
        self.label_stack.setStyleSheet("image: url(:/imgs/imgs/label_bg.png); color: 'white'")
        self.label_stack.setAlignment(Qt.AlignCenter)
        self.label_stack.setObjectName("label_stack")
        self.label_stack.setText("Stack")
        self.glayout_wp.addWidget(self.label_stack, 2, 0, 1, 1)
        self.hide()

        for row, stretch in [(0, 5), (1, 2), (2, 2)]:
            self.glayout_wp.setColumnStretch(row, stretch)

        if self.p_0:
            self.p_0_cards = widget_cards_player()

    def hide_cards(self):
        self.pix_cards.hide()

    def show_cards(self):
        self.pix_cards.show()

    def is_speaking(self):
        self.actual_cards = self.half_cards_purple
        self.resizeCards()

    def is_all_in(self):
        self.actual_cards = self.half_cards_red
        self.resizeCards()

    def won(self):
        self.actual_cards = self.half_cards_yellow
        self.resizeCards()

    def is_not_speaking_and_did_not_win(self):
        self.actual_cards = self.half_cards
        self.resizeCards()

    def resizeEvent(self, e):
        w = self.resizeCards()
        font = self.label_name.font()
        font.setPointSize(0.11 * w)
        self.label_name.setFont(font)
        self.label_stack.setFont(font)

    def resizeCards(self):
        w = self.width()
        self.pix_cards.setPixmap(self.actual_cards.scaledToWidth(0.7 * w))
        return w


class widget_front(QWidget):

    def __init__(self, parent=None, name='widget_front', empty=False):

        QWidget.__init__(self, parent)
        self.setObjectName(name)
        self.glayout_front = QGridLayout(self)
        self.glayout_front.setContentsMargins(0, 0, 0, 0)
        self.glayout_front.setObjectName("glayout_front")


        self.label_dealer = QLabel(self)
        self.label_dealer.setSizePolicy(sizePolicy)
        self.label_dealer.setText("")
        self.dealer_button = QPixmap(":/imgs/imgs//dealer_button_small.png")
        self.label_dealer.setPixmap(self.dealer_button)
        self.label_dealer.setScaledContents(False)
        self.label_dealer.setObjectName("label_2")
        self.label_dealer.hide()
        self.glayout_front.addWidget(self.label_dealer, 0, 0, 1, 1)

        self.widget_ogb = widget_ogb(self)
        self.glayout_front.addWidget(self.widget_ogb, 0, 1, 1, 1)

        self.glayout_front.setColumnStretch(0, 1)
        self.glayout_front.setColumnStretch(1, 3)

    def resizeEvent(self, e):
        w = 0.15 * self.width()
        self.label_dealer.setPixmap(self.dealer_button.scaledToWidth(w))

    def paintEvent(self, pe):
        """Nécessaire de redéfinir le paintEvent pour appliquer les stylesheet des custom widgets"""
        custom_paintEvent(self, pe)

class widget_ogb(QWidget):

    resized = pyqtSignal()

    def __init__(self, parent=None, pot=False):

        QWidget.__init__(self, parent)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(0, 0))
        self.setMaximumSize(QSize(169, 151))
        if pot:
            ss = "QWidget#widget_ogb{image: url(:/imgs/imgs/player0_stack.png)}"
        else:
            ss = "QWidget#widget_ogb{image: url(:/imgs/imgs/player_ogb.png)}"
        self.setStyleSheet(ss)
        self.setObjectName("widget_ogb")

        self.glayout_ogb = QGridLayout(self)
        self.glayout_ogb.setObjectName("glayout_ogb")

        self.label = QLabel(self)
        self.label.setText('')
        self.label.setSizePolicy(sizePolicy)
        self.label.setStyleSheet("color: 'white' ")
        self.label.setObjectName("label")
        self.glayout_ogb.addWidget(self.label, 0, 1, 1, 1)

        self.spacer = widget_empty()
        self.glayout_ogb.addWidget(self.spacer, 0, 0, 1, 1)
        self.hide()

    def resizeEvent(self, e):
        w = self.label.width()
        font = self.label.font()
        font.setPointSize(0.5 * w + 2)
        self.label.setFont(font)


    def paintEvent(self, pe):
        """Nécessaire de redéfinir le paintEvent pour appliquer les stylesheet des custom widgets"""
        custom_paintEvent(self, pe)

class widget_table_cards(QWidget):

    def __init__(self, parent):

        QWidget.__init__(self, parent)
        self.setObjectName("table_cards")
        self.setSizePolicy(sizePolicy)

        self.nb_shown_cards = None

        self.hlayout = QHBoxLayout(self)
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.setObjectName("hlayout")

        self.widget_pot = widget_ogb(self, pot=True)
        self.hlayout.addWidget(self.widget_pot)
        
        self.table_cards = [QLabel(self) for _ in range(5)]

        for card in self.table_cards:
            card.setPixmap(QPixmap(":/imgs/imgs/cards_imgs/14_0.png"))
            card.setScaledContents(True)
            card.setMinimumSize(20, 20)
            self.hlayout.addWidget(card)
            card.setSizePolicy(sizePolicy)
            card.hide()

        for column in range(6):
            stretch = 4 if column == 0 else 3
            self.hlayout.setStretch(column, stretch)

    def resizeEvent(self, e):
        w, h = self.parentWidget().width(), self.parentWidget().height()
        for card in self.table_cards:
            card.setMaximumSize(0.1*w, 0.15*h)


    def new_game(self):
        for card in self.table_cards:
            card.hide()
        self.nb_shown_cards = 0
        self.widget_pot.label.setText('')
        self.widget_pot.hide()

    def set_cards(self, cards):
        for ind in range(len(cards)):
            if ind >= self.nb_shown_cards:
                self.table_cards[ind].setPixmap(QPixmap(card_img(cards[ind])))
                self.table_cards[ind].show()
                self.nb_shown_cards += 1


class widget_table(QWidget):



    def __init__(self, parent):

        QWidget.__init__(self, parent)
        self.setSizePolicy(sizePolicy)

        self.setSizeIncrement(QSize(1, 1))
        self.setObjectName("widget_table")
        self.setStyleSheet("QWidget#widget_table{image: url(:/imgs/imgs/poker_table.png);}")

        self.glayout_table = QGridLayout(self)
        self.glayout_table.setContentsMargins(0, 0, 0, 0)
        self.glayout_table.setObjectName("glayout_table")

        self.widget_players = [None] * 7
        self.widget_fronts = [None] * 7

        for ind in range(7):
            self.create_widgets_players_and_fronts(ind)

        self.table_cards = widget_table_cards(self)
        self.glayout_table.addWidget(self.table_cards, 2, 2, 1, 3)

        for column, stretch in [(0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10)]:
            self.glayout_table.setColumnStretch(column, stretch)
        for row, stretch in [(0, 10), (1, 10), (2, 20), (3, 10), (4, 10)]:
            self.glayout_table.setRowStretch(row, stretch)

    def create_widgets_players_and_fronts(self, ind):
        po_players = [(4, 3), (3, 0), (1, 0), (0, 2), (0, 4), (1, 6), (3, 6)]
        po_fronts = [(3, 3), (3, 1), (1, 1), (1, 2), (1, 4), (1, 5), (3, 5)]
        alignment_dict = {'0': Qt.AlignBottom, '12': Qt.AlignRight, '34': Qt.AlignTop, '56': Qt.AlignLeft}
        align = lambda x: [alignment_dict[key] for key in alignment_dict.keys() if str(x) in key][0]

        p0 = True if ind == 0 else False
        ppx, ppy = po_players[ind]
        pfx, pfy = po_fronts[ind]
        self.widget_players[ind] = widget_player(parent=self, name="widget_player_"+str(ind), empty=False, p_0=p0)
        self.widget_fronts[ind] = widget_front(parent=self, name="widget_front_"+str(ind), empty=False)
        self.glayout_table.addWidget(self.widget_players[ind], ppx, ppy, 1, 1)
        self.glayout_table.addWidget(self.widget_fronts[ind], pfx, pfy, 1, 1, align(ind))
        self.widget_players[ind].hide()
        self.widget_fronts[ind].hide()


    def clear_ogbs(self):
        for widget_front in self.widget_fronts:
            widget_front.widget_ogb.hide()
            widget_front.widget_ogb.label.setText('')

    def paintEvent(self, pe):
        """Nécessaire de redéfinir le paintEvent pour appliquer les stylesheet des custom widgets"""
        custom_paintEvent(self, pe)



class widget_game(QWidget):
    """
    Disposé de la manière suivante:
    vlayout_game:       - widget_game
                        - hlayout_slider
                        - hlayout_buttons
    """

    def __init__(self, parent=None, server=None):

        QWidget.__init__(self, parent)
        self.server = server
        self.setObjectName("widget_game")
        self.resize(1000, 700)
        self.setMinimumSize(QSize(300, 200))
        self.setMaximumSize(QSize(4022, 16777215))
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.setStyleSheet("")
        self.reboot()

    def reboot(self):

        self.vlayout_game = QVBoxLayout(self)
        self.vlayout_game.setObjectName("vlayout_game")

        self.widget_table = widget_table(self)
        self.vlayout_game.addWidget(self.widget_table)

        self.hlayout_slider = QHBoxLayout()
        self.hlayout_slider.setObjectName("hlayout_slider")
        self.spacer_slider_left = widget_empty(name="spacer_slider_left", parent=self, hstretch=3)
        self.hlayout_slider.addWidget(self.spacer_slider_left)

        self.slider = QSlider(self)
        self.slider.setSizePolicy(sizePolicy)
        self.slider.setStyleSheet("")
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.slider.setValue(0)
        self.slider.setEnabled(False)
        self.slider.setMaximum(0)
        self.slider.valueChanged.connect(self.slider_to_text)
        self.hlayout_slider.addWidget(self.slider)

        self.spacer_slider_middle = widget_empty(name="spacer_slider_middle", parent=self, hstretch=1)
        self.hlayout_slider.addWidget(self.spacer_slider_middle)

        self.text_slider = QTextEdit(self)
        self.text_slider.setSizePolicy(sizePolicy)
        self.text_slider.setMinimumSize(QSize(20, 30))
        self.text_slider.setMaximumSize(QSize(60, 30))
        self.text_slider.setStyleSheet("border-color: rgb(252, 229, 9);")
        self.text_slider.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_slider.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_slider.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.text_slider.setObjectName("text_slider")
        self.text_slider.setReadOnly(True)
        self.hlayout_slider.addWidget(self.text_slider)

        self.spacer_slider_right = widget_empty(name="spacer_slider_right", parent=self, hstretch=1)
        self.hlayout_slider.addWidget(self.spacer_slider_right)

        for pos, stretch in (0, 3), (1, 8), (2, 2), (3, 2), (4, 2):
            self.hlayout_slider.setStretch(pos, stretch)

        self.vlayout_game.addLayout(self.hlayout_slider)

        self.hlayout_buttons = QHBoxLayout()
        self.hlayout_buttons.setObjectName("hlayout_buttons")

        self.button_fold = QPushButton(self)
        self.button_fold.clicked.connect(self.send_fold)
        self.button_call = QPushButton(self)
        self.button_call.clicked.connect(self.send_call)
        self.button_raise = QPushButton(self)
        self.button_raise.clicked.connect(self.send_raise)


        button_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        button_policy.setHorizontalStretch(10)
        button_policy.setVerticalStretch(0)
        for button, text, ss in [(self.button_fold, 'Fold', "color: white;background-color:rgb(216, 0, 5);"),
                                 (self.button_call, 'Call', "background-color: rgb(15, 103, 1);color: 'white'"),
                                 (self.button_raise, 'Raise', "background-color: rgb(253, 231, 44);color: 'white'")]:
            button_policy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
            button.setObjectName('button_' + text.lower())
            button.setSizePolicy(button_policy)
            button.setText(text)
            button.setStyleSheet(ss)

        self.button_spacer_1 = widget_empty(name="button_spacer_1", parent=self, hstretch=3)
        self.button_spacer_2 = widget_empty(name="button_spacer_2", parent=self, hstretch=1)
        self.button_spacer_3 = widget_empty(name="button_spacer_3", parent=self, hstretch=1)
        self.button_spacer_4 = widget_empty(name="button_spacer_4", parent=self, hstretch=3)

        for widget in [self.button_spacer_1, self.button_fold, self.button_spacer_2, self.button_call,
                       self.button_spacer_3,
                       self.button_raise, self.button_spacer_4]:
            self.hlayout_buttons.addWidget(widget)

        self.vlayout_game.addLayout(self.hlayout_buttons)

        self.vlayout_game.setStretch(0, 18)
        self.vlayout_game.setStretch(1, 0)
        self.vlayout_game.setStretch(2, 3)

        QMetaObject.connectSlotsByName(self)

    def slider_to_text(self):
        value = self.slider.value()
        self.text_slider.setText(str(value))

    @pyqtSlot()
    def send_raise(self):
        value = self.slider.value()
        send_server({'flag': 'action', 'action': value}, self.server)
        self.enable_all(False)

    @pyqtSlot()
    def send_fold(self):
        send_server({'flag': 'action', 'action': 'f'}, self.server)
        self.enable_all(False)

    @pyqtSlot()
    def send_call(self):
        send_server({'flag': 'action', 'action': 'c'}, self.server)
        self.enable_all(False)

    def enable_all(self, value):
        if not value:
            self.is_my_turn = False
        for widget in (self.button_fold, self.button_raise, self.button_call, self.slider, self.text_slider):
            widget.setEnabled(value)
        if not value:
            self.slider.setMinimum(0)
            self.slider.setValue(0)
            self.text_slider.setText('')

    def action(self, stack, ogb, amount_to_call):
        self.is_my_turn = True
        self.slider.setMinimum(amount_to_call)
        self.slider.setValue(amount_to_call)
        self.slider.setMaximum(stack + ogb)
        self.enable_all(True)

    def resizeEvent(self, e):
        w = self.button_fold.width()
        font = self.button_fold.font()
        font.setPointSize(0.07 * w)
        self.button_fold.setFont(font)
        self.button_raise.setFont(font)
        self.button_call.setFont(font)


def custom_paintEvent(parent, pe):
    """Nécessaire de redéfinir le paintEvent pour appliquer les stylesheet des custom widgets"""
    opt = QStyleOption()
    opt.initFrom(parent)
    p = QPainter(parent)
    s = parent.style()
    s.drawPrimitive(QStyle.PE_Widget, opt, p, parent)

def card_img(card):
    value, suit = card
    return f":/imgs/imgs/cards_imgs/{value}_{suit}.png"


sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
sizePolicy.setHorizontalStretch(0)
sizePolicy.setVerticalStretch(0)
sizePolicy.setHeightForWidth(True)
sizePolicy.setRetainSizeWhenHidden(True)
