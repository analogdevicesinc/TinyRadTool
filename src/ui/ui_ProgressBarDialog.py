# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ProgressBarDialog(object):
    def setupUi(self, ProgressBarDialog):
        ProgressBarDialog.setObjectName(_fromUtf8("ProgressBarDialog"))
        ProgressBarDialog.resize(197, 48)
        self.horizontalLayout = QtGui.QHBoxLayout(ProgressBarDialog)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.progressBar = QtGui.QProgressBar(ProgressBarDialog)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout.addWidget(self.progressBar)

        self.retranslateUi(ProgressBarDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressBarDialog)

    def retranslateUi(self, ProgressBarDialog):
        ProgressBarDialog.setWindowTitle(_translate("ProgressBarDialog", "Dialog", None))

