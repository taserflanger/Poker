# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'basic_poker.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import time
import threading
import main


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(380, 30, 200, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(670, 130, 200, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(660, 380, 200, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(380, 510, 200, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(70, 380, 200, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(70, 130, 200, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(350, 50, 200, 20))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(619, 160, 200, 20))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(640, 400, 200, 20))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(360, 490, 200, 20))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(60, 400, 200, 16))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(50, 150, 200, 16))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(90, 200, 800, 20))
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(360, 70, 200, 16))
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(509, 160, 200, 20))
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setGeometry(QtCore.QRect(529, 360, 200, 20))
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(370, 460, 200, 16))
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setGeometry(QtCore.QRect(170, 380, 200, 16))
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(self.centralwidget)
        self.label_19.setGeometry(QtCore.QRect(160, 135, 200, 16))
        self.label_19.setObjectName("label_19")
        self.label_20 = QtWidgets.QLabel(self.centralwidget)
        self.label_20.setGeometry(QtCore.QRect(90, 220, 800, 20))
        self.label_20.setObjectName("label_20")
        self.label_21 = QtWidgets.QLabel(self.centralwidget)
        self.label_21.setGeometry(QtCore.QRect(370, 10, 200, 16))
        self.label_21.setObjectName("label_21")
        self.label_22 = QtWidgets.QLabel(self.centralwidget)
        self.label_22.setGeometry(QtCore.QRect(619, 110, 200, 20))
        self.label_22.setObjectName("label_22")
        self.label_23 = QtWidgets.QLabel(self.centralwidget)
        self.label_23.setGeometry(QtCore.QRect(629, 350, 200, 20))
        self.label_23.setObjectName("label_23")
        self.label_24 = QtWidgets.QLabel(self.centralwidget)
        self.label_24.setGeometry(QtCore.QRect(360, 530, 200, 16))
        self.label_24.setObjectName("label_24")
        self.label_25 = QtWidgets.QLabel(self.centralwidget)
        self.label_25.setGeometry(QtCore.QRect(70, 360, 200, 16))
        self.label_25.setObjectName("label_25")
        self.label_26 = QtWidgets.QLabel(self.centralwidget)
        self.label_26.setGeometry(QtCore.QRect(60, 110, 200, 16))
        self.label_26.setObjectName("label_26")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        global table
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", table.players[0].name))
        self.label_2.setText(_translate("MainWindow", table.players[1].name))
        self.label_3.setText(_translate("MainWindow", table.players[2].name))
        self.label_4.setText(_translate("MainWindow", table.players[3].name))
        self.label_5.setText(_translate("MainWindow", table.players[4].name))
        self.label_6.setText(_translate("MainWindow", table.players[5].name))

        self.label_7.setText(_translate("MainWindow", "Player 1 - cards"))
        self.label_8.setText(_translate("MainWindow", "Player 2 - cards"))
        self.label_9.setText(_translate("MainWindow", "Player 3 - cards"))
        self.label_10.setText(_translate("MainWindow", "Player 4 - cards"))
        self.label_11.setText(_translate("MainWindow", "Player 5 - cards"))
        self.label_12.setText(_translate("MainWindow", "Player 6 - cards"))

        self.label_13.setText(_translate("MainWindow", "Table - cards"))

        self.label_14.setText(_translate("MainWindow", "Player 1 - ogb"))
        self.label_15.setText(_translate("MainWindow", "Player 2 - ogb"))
        self.label_16.setText(_translate("MainWindow", "Player 3 - ogb"))
        self.label_17.setText(_translate("MainWindow", "Player 4 - ogb"))
        self.label_18.setText(_translate("MainWindow", "Player 5 - ogb"))
        self.label_19.setText(_translate("MainWindow", "Player 6 - ogb"))

        self.label_20.setText(_translate("MainWindow", "Table - pot"))

        self.label_21.setText(_translate("MainWindow", "Player 1 - stack"))
        self.label_22.setText(_translate("MainWindow", "Player 2 - stack"))
        self.label_23.setText(_translate("MainWindow", "Player 3 - stack"))
        self.label_24.setText(_translate("MainWindow", "Player 4 - stack"))
        self.label_25.setText(_translate("MainWindow", "Player 5 - stack"))
        self.label_26.setText(_translate("MainWindow", "Player 6 - stack"))

    def change_all(self):
        global table
        self.label_7.setText(str([str(card) for card in table.players[0].hand]))
        #self.imgcard.setPixmap(QtGui.QPixmap(table.players[0].hand[0]))
        self.label_8.setText(str([str(card) for card in table.players[1].hand]))
        self.label_9.setText(str([str(card) for card in table.players[2].hand]))
        self.label_10.setText(str([str(card) for card in table.players[3].hand]))
        self.label_11.setText(str([str(card) for card in table.players[4].hand]))
        self.label_12.setText(str([str(card) for card in table.players[5].hand]))

        self.label_13.setText(str([str(card) for card in table.cards]))

        self.label_14.setText('mise : ' + str(table.players[0].on_going_bet))
        self.label_15.setText('mise : ' + str(table.players[1].on_going_bet))
        self.label_16.setText('mise : ' + str(table.players[2].on_going_bet))
        self.label_17.setText('mise : ' + str(table.players[3].on_going_bet))
        self.label_18.setText('mise : ' + str(table.players[4].on_going_bet))
        self.label_19.setText('mise : ' + str(table.players[5].on_going_bet))

        self.label_20.setText(str([pot for pot in table.pots]))

        self.label_21.setText('stack : ' + str(table.players[0].stack))
        self.label_22.setText('stack : ' + str(table.players[1].stack))
        self.label_23.setText('stack : ' + str(table.players[2].stack))
        self.label_24.setText('stack : ' + str(table.players[3].stack))
        self.label_25.setText('stack : ' + str(table.players[4].stack))
        self.label_26.setText('stack : ' + str(table.players[5].stack))

def redraw_gui():
    global ui
    while True:
        ui.change_all()
        time.sleep(1)

if __name__ == "__main__":
    import sys
    table = main.main(GUI=True)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    x = threading.Thread(target=redraw_gui)
    x.start()

    y = threading.Thread(target=table.set)
    y.start()

    MainWindow.show()

    sys.exit(app.exec_())



