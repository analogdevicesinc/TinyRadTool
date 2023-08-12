# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setupBoard.ui'
#
# Created: Wed May 27 07:46:33 2015
#      by: PyQt4-uic 0.2.15 running on PyQt4 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SetupBoard(object):
    def setupUi(self, SetupBoard):
        SetupBoard.setObjectName("SetupBoard")
        SetupBoard.setWindowTitle("TinyRadTool Configuration")
        SetupBoard.resize(332, 187)
        self.verticalLayout = QtGui.QVBoxLayout(SetupBoard)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtGui.QLabel(SetupBoard)
        self.label.setMinimumSize(QtCore.QSize(150, 0))
        self.label.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.lineEdit_ipaddress = QtGui.QLineEdit(SetupBoard)
        self.lineEdit_ipaddress.setMinimumSize(QtCore.QSize(150, 0))
        self.lineEdit_ipaddress.setMaximumSize(QtCore.QSize(150, 16777215))
        self.lineEdit_ipaddress.setObjectName("lineEdit_ipaddress")
        self.horizontalLayout_3.addWidget(self.lineEdit_ipaddress)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(SetupBoard)
        self.label_2.setMinimumSize(QtCore.QSize(150, 0))
        self.label_2.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lineEdit_port = QtGui.QLineEdit(SetupBoard)
        self.lineEdit_port.setMinimumSize(QtCore.QSize(80, 0))
        self.lineEdit_port.setMaximumSize(QtCore.QSize(80, 16777215))
        self.lineEdit_port.setObjectName("lineEdit_port")
        self.horizontalLayout_2.addWidget(self.lineEdit_port)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.label_file_not_found = QtGui.QLabel(SetupBoard)
        self.label_file_not_found.setObjectName("label_file_not_found")
        self.horizontalLayout_4.addWidget(self.label_file_not_found)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.pushButton_apply = QtGui.QPushButton(SetupBoard)
        self.pushButton_apply.setObjectName("pushButton_apply")
        self.horizontalLayout.addWidget(self.pushButton_apply)
        self.pushButton_cancel = QtGui.QPushButton(SetupBoard)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.horizontalLayout.addWidget(self.pushButton_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SetupBoard)
        QtCore.QMetaObject.connectSlotsByName(SetupBoard)

    def retranslateUi(self, SetupBoard):
        SetupBoard.setWindowTitle(QtGui.QApplication.translate("SetupBoard", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SetupBoard", "IP Address", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SetupBoard", "Port", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_apply.setText(QtGui.QApplication.translate("SetupBoard", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_cancel.setText(QtGui.QApplication.translate("SetupBoard", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

