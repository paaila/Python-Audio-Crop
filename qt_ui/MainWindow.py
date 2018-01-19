# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(870, 553)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.file_list = QtWidgets.QListView(self.centralwidget)
        self.file_list.setObjectName("file_list")
        self.horizontalLayout.addWidget(self.file_list)
        self.widget_tab = QtWidgets.QTabWidget(self.centralwidget)
        self.widget_tab.setObjectName("widget_tab")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.button_record = QtWidgets.QPushButton(self.tab)
        self.button_record.setGeometry(QtCore.QRect(10, 80, 85, 26))
        self.button_record.setObjectName("button_record")
        self.button_pause = QtWidgets.QPushButton(self.tab)
        self.button_pause.setGeometry(QtCore.QRect(120, 80, 85, 26))
        self.button_pause.setObjectName("button_pause")
        self.button_seek = QtWidgets.QPushButton(self.tab)
        self.button_seek.setGeometry(QtCore.QRect(70, 160, 85, 26))
        self.button_seek.setObjectName("button_seek")
        self.input_seek = QtWidgets.QLineEdit(self.tab)
        self.input_seek.setGeometry(QtCore.QRect(30, 30, 113, 24))
        self.input_seek.setObjectName("input_seek")
        self.progressBar = QtWidgets.QProgressBar(self.tab)
        self.progressBar.setGeometry(QtCore.QRect(50, 220, 118, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.widget_tab.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.widget_tab.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.widget_tab)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 870, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.widget_tab.setCurrentIndex(0)
        self.button_record.clicked.connect(MainWindow.toggle_stop)
        self.button_pause.clicked.connect(MainWindow.toggle_pause)
        self.button_seek.clicked.connect(MainWindow.seek)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_record.setText(_translate("MainWindow", "Start"))
        self.button_pause.setText(_translate("MainWindow", "Pause"))
        self.button_seek.setText(_translate("MainWindow", "set_position"))
        self.widget_tab.setTabText(self.widget_tab.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.widget_tab.setTabText(self.widget_tab.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))

