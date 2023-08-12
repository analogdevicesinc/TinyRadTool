# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'strtup.ui'
#
# Created: Tue Mar 29 12:52:31 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_Strtup(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(508, 479)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.Label_Header = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Label_Header.setFont(font)
        self.Label_Header.setObjectName(_fromUtf8("Label_Header"))
        self.verticalLayout_3.addWidget(self.Label_Header)
        spacerItem = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setMidLineWidth(1)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_3.addWidget(self.label_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.ChkBox_Agree = QtWidgets.QCheckBox(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ChkBox_Agree.setFont(font)
        self.ChkBox_Agree.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.ChkBox_Agree.setObjectName(_fromUtf8("ChkBox_Agree"))
        self.verticalLayout_3.addWidget(self.ChkBox_Agree, QtCore.Qt.AlignRight)
        self.WidgetPic = QtWidgets.QWidget(Dialog)
        self.WidgetPic.setObjectName(_fromUtf8("WidgetPic"))
        self.verticalLayout_3.addWidget(self.WidgetPic)
        spacerItem2 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem2)
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.ComboBox_Select = QtWidgets.QComboBox(Dialog)
        self.ComboBox_Select.setObjectName(_fromUtf8("ComboBox_Select"))
        self.verticalLayout_3.addWidget(self.ComboBox_Select)
        spacerItem3 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.Button_Ok = QtWidgets.QPushButton(Dialog)
        self.Button_Ok.setObjectName(_fromUtf8("Button_Ok"))
        self.horizontalLayout.addWidget(self.Button_Ok)
        self.Button_Cancel = QtWidgets.QPushButton(Dialog)
        self.Button_Cancel.setObjectName(_fromUtf8("Button_Cancel"))
        self.horizontalLayout.addWidget(self.Button_Cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "TinyRadTool Configuration", None))
        self.Label_Header.setText(_translate("Dialog", "TinyRadTool (1.1.2) © Analog Devices 2023", None))
        palette     = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.label_2.setPalette(palette)  
        self.label_2.setText(_translate("Dialog", "The TinyRad is distributed as evaluation platform. The user is responsible for operation according to regulatory issues for frequency and transmit power.", None))
        self.ChkBox_Agree.setText(_translate("Dialog", "I agree", None))
        self.label.setText(_translate("Dialog", "Available configuration files in C:/Tools/TinyRadTool/", None))
        self.Button_Ok.setText(_translate("Dialog", "Ok", None))
        self.Button_Cancel.setText(_translate("Dialog", "Cancel", None))

