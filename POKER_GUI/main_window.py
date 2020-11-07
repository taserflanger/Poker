# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class main_window(QtWidgets.QMainWindow):
    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)

        self.setObjectName("main_window")
        self.setWindowTitle("PSL Poker")
        self.resize(900, 680)
        self.setMinimumSize(QtCore.QSize(300, 230))

        # self.centralwidget = QtWidgets.QWidget(self)
        # self.centralwidget.setObjectName("centralwidget")
        # self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        # self.horizontalLayout.setObjectName("horizontalLayout")
        # self.setCentralWidget(self.centralwidget)

        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 900, 22))
        self.menu_bar.setObjectName("menu_bar")
        self.menu_options = QtWidgets.QMenu(self.menu_bar)
        self.menu_options.setObjectName("menu_options")
        self.setMenuBar(self.menu_bar)

        self.action_accueil = QtWidgets.QAction(self)
        self.action_accueil.setEnabled(False)
        self.action_accueil.setObjectName("action_accueil")
        self.action_accueil.setText("Accueil")

        self.action_quitter = QtWidgets.QAction(self)
        self.action_quitter.setEnabled(False)
        self.action_quitter.setObjectName("action_quitter")
        self.action_quitter.setText("Quitter")

        self.menu_options.addAction(self.action_accueil)
        self.menu_options.addAction(self.action_quitter)
        self.menu_options.setTitle("Options")
        self.menu_bar.addAction(self.menu_options.menuAction())

        QtCore.QMetaObject.connectSlotsByName(self)
