# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_fwupgrd.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_UpgradeDialog(object):
    def setupUi(self, UpgradeDialog):
        UpgradeDialog.setObjectName(_fromUtf8("UpgradeDialog"))
        UpgradeDialog.resize(481, 597)
        self.verticalLayout = QtWidgets.QVBoxLayout(UpgradeDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtWidgets.QLabel(UpgradeDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label_4 = QtWidgets.QLabel(UpgradeDialog)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_2.addWidget(self.label_4)
        self.checkBox_agree = QtWidgets.QCheckBox(UpgradeDialog)
        self.checkBox_agree.setObjectName(_fromUtf8("checkBox_agree"))
        self.verticalLayout_2.addWidget(self.checkBox_agree)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.label = QtWidgets.QLabel(UpgradeDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_5 = QtWidgets.QLabel(UpgradeDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_3.addWidget(self.label_5)
        self.comboBox_select_image = QtWidgets.QComboBox(UpgradeDialog)
        self.comboBox_select_image.setMinimumSize(QtCore.QSize(160, 0))
        self.comboBox_select_image.setObjectName(_fromUtf8("comboBox_select_image"))
        self.horizontalLayout_3.addWidget(self.comboBox_select_image)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_2 = QtWidgets.QLabel(UpgradeDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.textBrowser_ReleaseNotes = QtWidgets.QTextBrowser(UpgradeDialog)
        self.textBrowser_ReleaseNotes.setObjectName(_fromUtf8("textBrowser_ReleaseNotes"))
        self.verticalLayout.addWidget(self.textBrowser_ReleaseNotes)
        self.label_6 = QtWidgets.QLabel(UpgradeDialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.textEdit_progress = QtWidgets.QTextEdit(UpgradeDialog)
        self.textEdit_progress.setObjectName(_fromUtf8("textEdit_progress"))
        self.verticalLayout.addWidget(self.textEdit_progress)
        self.progressBar_progress = QtWidgets.QProgressBar(UpgradeDialog)
        self.progressBar_progress.setProperty("value", 24)
        self.progressBar_progress.setObjectName(_fromUtf8("progressBar_progress"))
        self.verticalLayout.addWidget(self.progressBar_progress)
        self.label_info = QtWidgets.QLabel(UpgradeDialog)
        self.label_info.setText(_fromUtf8(""))
        self.label_info.setObjectName(_fromUtf8("label_info"))
        self.verticalLayout.addWidget(self.label_info)
        spacerItem2 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.pushButton_start_upgrade = QtWidgets.QPushButton(UpgradeDialog)
        self.pushButton_start_upgrade.setObjectName(_fromUtf8("pushButton_start_upgrade"))
        self.horizontalLayout.addWidget(self.pushButton_start_upgrade)
        self.pushButton_close = QtWidgets.QPushButton(UpgradeDialog)
        self.pushButton_close.setObjectName(_fromUtf8("pushButton_close"))
        self.horizontalLayout.addWidget(self.pushButton_close)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_5.raise_()
        self.label_5.raise_()
        self.comboBox_select_image.raise_()
        self.label_6.raise_()

        self.retranslateUi(UpgradeDialog)
        QtCore.QMetaObject.connectSlotsByName(UpgradeDialog)

    def retranslateUi(self, UpgradeDialog):
        UpgradeDialog.setWindowTitle(_translate("UpgradeDialog", "Firmware Upgrade", None))
        self.label_3.setText(_translate("UpgradeDialog", "READ THIS FIRST!", None))
        self.label_4.setText(_translate("UpgradeDialog", "Once the firmware update process has been started, it cannot be interrupted. Disconnecting the power supply or the USB connection results in a broken system which can only be reset to its original state with a JTAG ICE-1000 programmer.", None))
        self.checkBox_agree.setText(_translate("UpgradeDialog", "I understand the risks & want to upgrade the DemoRad firmware now", None))
        self.label.setText(_translate("UpgradeDialog", "Firmware Images must be placed in the same directory where the TinyRadTool is executed from. Firmware images found will be selectable in the list below.", None))
        self.label_5.setText(_translate("UpgradeDialog", "Select Firmware Image", None))
        self.label_2.setText(_translate("UpgradeDialog", "Firmware Image Info", None))
        self.label_6.setText(_translate("UpgradeDialog", "Upgrade Progress", None))
        self.pushButton_start_upgrade.setText(_translate("UpgradeDialog", "Start Upgrade", None))
        self.pushButton_close.setText(_translate("UpgradeDialog", "Close", None))

