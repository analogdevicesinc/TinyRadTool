from PyQt5 import QtCore, QtGui, QtWidgets
import  src.ui.ui_setupBoard as ui_setupBoard
import  re


class SetupBoard(QtWidgets.QDialog, ui_setupBoard.Ui_SetupBoard):

    def __init__(self, patre):
        super(SetupBoard, self).__init__()
        self.patre  = patre
        self.setupUi(self)
        self.initLabels()
        self.assignWidgets()
        self.CenterWindow()

    def assignWidgets(self):
        self.pushButton_apply.clicked.connect(self.pushButton_apply_clicked)
        self.pushButton_cancel.clicked.connect(self.pushButton_cancel_clicked)

    def CenterWindow(self):
        screen              = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint         = QtGui.QApplication.desktop().screenGeometry(screen).center()
        self.move(centerPoint.x() - self.width() * 0.5, centerPoint.y() - self.height() * 0.5)

    def pushButton_apply_clicked(self):
        stIp        =   self.lineEdit_ipaddress.text()
        RegExp      =   re.compile(r"(?P<Val>([0-9]{1,3}[.]{1,1}[0-9]{1,3}[.]{1,1}[0-9]{1,3}[.]{1,1}[0-9]{1,3}))")
        Match       =   RegExp.search(stIp)
        if Match:
            self.patre.GuiIpAddr    =   Match.group("Val")
            print("Valid Address found", self.patre.GuiIpAddr)

        self.accept()

    def pushButton_cancel_clicked(self):
        self.reject()

    def initLabels(self):
        self.setWindowTitle("Board Network Configuration")
        self.lineEdit_ipaddress.setText(str(self.patre.GuiIpAddr))
        self.lineEdit_port.setText(str(self.patre.GuiCfgPortNr))