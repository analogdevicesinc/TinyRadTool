import os
from PyQt5 import QtCore, QtGui, QtWidgets
import src.ui.ui_about as ui_about

""" AboutDialog handler
Calls the UI Class Dialog
"""
class AboutDialog(QtWidgets.QDialog, ui_about.Ui_AboutDialog):

    def __init__(self):
        super(AboutDialog, self).__init__()
        self.setupUi(self)
        #self.setStyleSheet("background-color: white;")
        path = os.path.join("src", "ressource", "img", "adi.png")
        self.Image_Logo = QtGui.QImage(path)
        self.Label_Logo = QtWidgets.QLabel()
        self.Logo_Layout = QtWidgets.QHBoxLayout()
        self.Label_Logo.setMaximumSize(174,87)
        self.Image_Logo.scaledToWidth(174)
        self.Label_Logo.setPixmap(QtGui.QPixmap.fromImage(self.Image_Logo))
        self.Logo_Layout.addWidget(self.Label_Logo)
        self.widget_pic.setLayout(self.Logo_Layout)
        self.label_version.setText("TinyRadTool 1.1.2")
        self.assignWidgets()
        self.center()


    def center(self):
        """ Moves the Dialog to the center of the screen """
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        self.move(centerPoint.x() - self.width() * 0.5, centerPoint.y() - self.height() * 0.5)


    def assignWidgets(self):
        """ Register close Button Signalhandler """
        self.pushButton_close.clicked.connect(self.pushButton_close_clicked)


    def pushButton_close_clicked(self):
        """ Called when the "close" pushbutton was pressed.
        closes the window
        """
        self.accept()
